"""
LLM Orchestration module — prompt building, LLM calls, and output validation.

Usage:
    from llm_orchestration import build_prompt, generate_cpp, check_syntax
    from llm_orchestration.prompt_builder import SYSTEM_PROMPT

    prompt = build_prompt(source_chunk, function_ir, graph_context)
    cpp_code = generate_cpp(SYSTEM_PROMPT, prompt, original_ir=[function_ir])
"""

from .prompt_builder import build_prompt, build_full_file_prompt, SYSTEM_PROMPT
from .llm_client import generate_cpp
from .validator import check_syntax, check_no_hallucinations

__all__ = [
    "build_prompt",
    "build_full_file_prompt",
    "SYSTEM_PROMPT",
    "generate_cpp",
    "check_syntax",
    "check_no_hallucinations",
]
