"""
Validates LLM-generated C++ output:
  1. Syntax validity (does it compile / parse as valid C++?)
  2. Structural fidelity (no hallucinated variables/functions not present
     in the original IR).
"""


def check_syntax(cpp_code: str) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    """
    # TODO: run through a C++ parser or `g++ -fsyntax-only` dry-run
    raise NotImplementedError


def check_no_hallucinations(cpp_code: str, original_ir) -> tuple[bool, list[str]]:
    """
    Returns (passed, list_of_flagged_symbols) by comparing symbols used in
    cpp_code against what's known from original_ir.
    """
    # TODO: implement symbol comparison
    raise NotImplementedError
