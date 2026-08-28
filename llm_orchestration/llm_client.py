"""
Thin wrapper around the Ollama REST API for local LLM code generation.

Uses Qwen2.5-Coder-3B-Instruct via Ollama at http://localhost:11434.
Includes retry/repair loop for failed validations.
"""

import json
import re
import logging

import requests

from .prompt_builder import SYSTEM_PROMPT
from .validator import check_syntax, check_no_hallucinations

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:3b"
DEFAULT_TIMEOUT = 120  # seconds — 3B model is fast but generation can be long
MAX_RETRIES = 3


def generate_cpp(
    system_prompt: str,
    user_prompt: str,
    original_ir=None,
    model: str = MODEL_NAME,
    temperature: float = 0.2,
) -> str:
    """
    Calls the Ollama LLM and returns the generated C++ code as a string.

    Args:
        system_prompt: the system instruction (role definition).
        user_prompt: the user prompt with source code and IR context.
        original_ir: optional list of FunctionNode for hallucination checking.
        model: Ollama model name (default: qwen2.5-coder:3b).
        temperature: sampling temperature (lower = more deterministic).

    Returns:
        The generated C++ code (stripped of markdown fences).

    Raises:
        RuntimeError: if LLM call fails or validation fails after max retries.
    """
    cpp_code = _call_ollama(system_prompt, user_prompt, model, temperature)
    cpp_code = _extract_code_block(cpp_code)

    if original_ir is None:
        return cpp_code

    # Validation + retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        issues = []

        # Syntax check
        syntax_ok, syntax_err = check_syntax(cpp_code)
        if not syntax_ok:
            issues.append(f"Syntax error: {syntax_err}")

        # Hallucination check
        halluc_ok, flagged = check_no_hallucinations(cpp_code, original_ir)
        if not halluc_ok:
            issues.append(f"Hallucinated symbols: {', '.join(flagged)}")

        if not issues:
            logger.info("Validation passed on attempt %d", attempt)
            return cpp_code

        if attempt >= MAX_RETRIES:
            logger.warning(
                "Validation failed after %d attempts. Returning best effort. Issues: %s",
                MAX_RETRIES, "; ".join(issues)
            )
            return cpp_code

        # Repair: re-prompt with error feedback
        logger.info("Attempt %d failed (%s), retrying...", attempt, "; ".join(issues))
        repair_prompt = _build_repair_prompt(user_prompt, cpp_code, issues)
        cpp_code = _call_ollama(system_prompt, repair_prompt, model, temperature)
        cpp_code = _extract_code_block(cpp_code)

    return cpp_code


def _call_ollama(
    system_prompt: str, user_prompt: str, model: str, temperature: float
) -> str:
    """Make a single call to the Ollama generate API."""
    payload = {
        "model": model,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,       # max output tokens
            "num_ctx": 4096,           # context window (conservative for 3B)
        },
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
    except requests.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_URL}. "
            "Make sure Ollama is running (`ollama serve`) and the model is pulled "
            f"(`ollama pull {model}`)."
        )
    except requests.Timeout:
        raise RuntimeError(
            f"Ollama request timed out after {DEFAULT_TIMEOUT}s. "
            "The model may be too slow or the input too large."
        )
    except requests.HTTPError as e:
        raise RuntimeError(f"Ollama API error: {e}")


def _extract_code_block(text: str) -> str:
    """Extract C++ code from markdown fenced code blocks."""
    # Try to find ```cpp ... ``` first
    pattern = r"```(?:cpp|c\+\+)?\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no fence found, return the raw text (LLM may have output plain code)
    return text.strip()


def _build_repair_prompt(original_prompt: str, bad_code: str, issues: list[str]) -> str:
    """Build a repair prompt asking the LLM to fix validation failures."""
    issue_text = "\n".join(f"- {issue}" for issue in issues)
    return f"""{original_prompt}

## Previous Attempt (has errors)
```cpp
{bad_code}
```

## Errors Found
{issue_text}

Please fix these errors and output the corrected C++ code in a ```cpp fence.
Preserve all original logic and variable names."""
