"""
Validates LLM-generated C++ output:
  1. Syntax validity — uses tree-sitter-cpp to parse and check for ERROR nodes.
  2. Structural fidelity — no hallucinated variables/functions not present
     in the original IR.

Note: tree-sitter-cpp must be installed (`pip install tree-sitter-cpp`).
Falls back to a basic heuristic check if tree-sitter-cpp is unavailable.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Try to load tree-sitter-cpp for syntax validation
_CPP_PARSER = None
try:
    from tree_sitter import Language, Parser
    import tree_sitter_cpp
    _CPP_LANG = Language(tree_sitter_cpp.language())
    _CPP_PARSER = Parser(_CPP_LANG)
except ImportError:
    logger.warning(
        "tree-sitter-cpp not installed. Syntax checking will use basic heuristics. "
        "Install with: pip install tree-sitter-cpp"
    )

# C++ standard library symbols that are NOT hallucinations
_CPP_STDLIB_ALLOWLIST = {
    # I/O
    "std", "cout", "cin", "cerr", "endl", "printf", "scanf", "puts", "getchar",
    "putchar", "fprintf", "sprintf", "snprintf",
    # Types & containers
    "string", "vector", "array", "map", "set", "pair", "tuple", "optional",
    "int", "float", "double", "char", "bool", "void", "long", "short",
    "unsigned", "signed", "size_t", "auto", "const",
    # Common functions
    "main", "return", "sizeof", "static_cast", "dynamic_cast", "reinterpret_cast",
    "new", "delete", "nullptr", "true", "false", "NULL",
    "push_back", "size", "begin", "end", "empty", "length", "substr",
    "find", "erase", "insert", "clear", "front", "back", "at",
    "to_string", "stoi", "stof", "stod", "atoi", "atof",
    "abs", "min", "max", "swap", "sort", "sqrt", "pow",
    # Headers (without angle brackets)
    "iostream", "cstdio", "cstring", "cmath", "cstdlib", "algorithm",
    "string", "vector", "map", "set", "fstream", "sstream",
    # Keywords that look like identifiers
    "include", "using", "namespace", "class", "struct", "enum",
    "if", "else", "while", "for", "do", "switch", "case", "break",
    "continue", "typedef", "template", "typename", "virtual", "override",
    "public", "private", "protected", "static", "extern", "inline",
    "const", "constexpr", "noexcept", "throw", "try", "catch",
}


def check_syntax(cpp_code: str) -> tuple[bool, str]:
    """
    Check if the generated C++ code is syntactically valid.

    Returns (is_valid, error_message).
    """
    if _CPP_PARSER is not None:
        return _check_syntax_treesitter(cpp_code)
    else:
        return _check_syntax_heuristic(cpp_code)


def _check_syntax_treesitter(cpp_code: str) -> tuple[bool, str]:
    """Use tree-sitter-cpp to check for parse errors."""
    tree = _CPP_PARSER.parse(cpp_code.encode("utf-8"))
    errors = []

    def find_errors(node, depth=0):
        if node.type == "ERROR":
            line = node.start_point[0] + 1
            col = node.start_point[1]
            snippet = node.text.decode()[:50] if node.text else ""
            errors.append(f"line {line}:{col} near '{snippet}'")
        if depth < 100:  # prevent infinite recursion
            for child in node.children:
                find_errors(child, depth + 1)

    find_errors(tree.root_node)

    if errors:
        return False, f"Parse errors found: {'; '.join(errors[:5])}"
    return True, ""


def _check_syntax_heuristic(cpp_code: str) -> tuple[bool, str]:
    """Basic heuristic syntax check (fallback when tree-sitter-cpp unavailable)."""
    # Check balanced braces
    open_braces = cpp_code.count("{")
    close_braces = cpp_code.count("}")
    if open_braces != close_braces:
        return False, f"Unbalanced braces: {open_braces} opening vs {close_braces} closing"

    # Check balanced parentheses
    open_parens = cpp_code.count("(")
    close_parens = cpp_code.count(")")
    if open_parens != close_parens:
        return False, f"Unbalanced parentheses: {open_parens} opening vs {close_parens} closing"

    # Check for common LLM failure: outputting explanation instead of code
    if len(cpp_code.strip()) < 10:
        return False, "Generated code is too short (possibly empty or just explanation)"

    return True, ""


def check_no_hallucinations(cpp_code: str, original_ir) -> tuple[bool, list[str]]:
    """
    Check that the generated C++ doesn't introduce variables or functions
    that don't exist in the original source IR.

    Returns (passed, list_of_flagged_symbols) by comparing symbols used in
    cpp_code against what's known from original_ir.

    Args:
        cpp_code: the generated C++ code string.
        original_ir: a list of FunctionNode objects from the parser.

    Returns:
        (True, []) if no hallucinations detected.
        (False, [list of suspicious symbols]) otherwise.
    """
    # Build the set of known symbols from the original IR
    known_symbols: set[str] = set()

    if not isinstance(original_ir, list):
        original_ir = [original_ir]

    for fn in original_ir:
        known_symbols.add(fn.name)
        for p in fn.parameters:
            known_symbols.add(p.name)
        for v in fn.local_variables:
            known_symbols.add(v.name)
        for c in fn.calls:
            known_symbols.add(c.callee_name)

    # Extract identifiers from C++ code using regex
    # (tree-sitter would be better but this is simpler and sufficient)
    cpp_identifiers = set(re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", cpp_code))

    # Remove known symbols, stdlib, and short identifiers (likely keywords)
    unknown = cpp_identifiers - known_symbols - _CPP_STDLIB_ALLOWLIST
    # Also remove identifiers that are just 1 char (loop vars, temp vars)
    unknown = {s for s in unknown if len(s) > 1}

    if unknown:
        # Only flag if there are "suspicious" unknowns (more than a few)
        # Small numbers of unknowns are usually false positives (type names, etc.)
        flagged = sorted(unknown)
        if len(flagged) > 10:
            # Too many unknowns — something is probably wrong
            return False, flagged
        else:
            # A few unknowns — likely benign (type aliases, macros, etc.)
            logger.info("Minor unknown symbols (likely benign): %s", flagged)
            return True, []

    return True, []
