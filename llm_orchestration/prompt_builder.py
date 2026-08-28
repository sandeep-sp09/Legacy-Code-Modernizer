"""
Builds prompts for the LLM by combining:
  - the original source chunk
  - the extracted IR (functions, variables, calls) from the parser module
  - relevant dependency-graph context (what this function calls / is called by)
"""

from parser.models import FunctionNode


SYSTEM_PROMPT = """You are a code modernization assistant. You convert legacy
Pascal/C source code into idiomatic, modern C++. You must preserve the exact
logic and behavior of the original code. Do not invent variables, functions,
or behavior that is not present in the original source or its stated context.

Rules:
- Output ONLY the C++ code, wrapped in a single ```cpp code fence.
- Use modern C++ features (auto, range-for, std::string, std::vector, etc.) where appropriate.
- Preserve all original function names, parameter names, and variable names.
- Add #include directives for any standard library headers used.
- Do not add main() unless the original code has one.
- Do not add explanatory comments about the conversion process."""


def build_prompt(source_chunk: str, function_ir: FunctionNode, graph_context: str) -> str:
    """
    Args:
        source_chunk: the raw original source code for this function/chunk.
        function_ir: parser.models.FunctionNode for this chunk.
        graph_context: short text description of related functions from the
            dependency graph (callers/callees).

    Returns:
        A fully-formed user prompt string to send to the LLM.
    """
    # Build a compact IR summary
    ir_summary = _format_ir(function_ir)

    prompt = f"""Convert the following {function_ir.language.upper()} code to modern, idiomatic C++.

## Original Source Code
```{function_ir.language}
{source_chunk.strip()}
```

## Extracted Structure (IR)
{ir_summary}

## Dependency Context
{graph_context}

## Instructions
Convert this code to modern C++. Preserve all logic, variable names, and function signatures exactly. Output only the C++ code in a ```cpp fence."""

    return prompt


def build_full_file_prompt(
    source_code: str,
    functions: list[FunctionNode],
    graph_context: str,
    language: str,
) -> str:
    """
    Build a prompt for converting an entire source file at once.
    Used when the file is small enough to fit in one prompt.

    Args:
        source_code: the full original source file text.
        functions: all FunctionNode IR objects extracted from the file.
        graph_context: combined graph context for all functions.
        language: "pascal" or "c".

    Returns:
        A fully-formed user prompt string.
    """
    ir_parts = [_format_ir(fn) for fn in functions]
    ir_summary = "\n\n".join(ir_parts)

    prompt = f"""Convert the following complete {language.upper()} source file to modern, idiomatic C++.

## Original Source Code
```{language}
{source_code.strip()}
```

## Extracted Structure (IR)
{ir_summary}

## Dependency Context
{graph_context}

## Instructions
Convert the entire file to a single modern C++ source file. Preserve all logic, variable names, and function signatures. Replace Pascal/C idioms with modern C++ equivalents (e.g., writeln -> std::cout, printf -> std::cout). Output only the C++ code in a ```cpp fence."""

    return prompt


def _format_ir(fn: FunctionNode) -> str:
    """Format a FunctionNode as a compact text summary for inclusion in a prompt."""
    lines = [f"Function: {fn.name} (lines {fn.start_line}-{fn.end_line})"]

    if fn.parameters:
        params = ", ".join(f"{p.name}: {p.var_type}" for p in fn.parameters)
        lines.append(f"  Parameters: {params}")

    if fn.local_variables:
        local_vars = ", ".join(f"{v.name}: {v.var_type}" for v in fn.local_variables)
        lines.append(f"  Local variables: {local_vars}")

    if fn.calls:
        call_names = ", ".join(f"{c.callee_name} (line {c.line})" for c in fn.calls)
        lines.append(f"  Calls: {call_names}")

    if fn.control_flow:
        cf = ", ".join(f"{c.kind} (lines {c.start_line}-{c.end_line})" for c in fn.control_flow)
        lines.append(f"  Control flow: {cf}")

    return "\n".join(lines)
