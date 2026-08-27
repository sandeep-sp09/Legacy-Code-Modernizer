"""
Walks the raw Tree-sitter AST and extracts a simplified intermediate
representation (IR) that downstream modules (dependency graph, LLM
orchestration) can consume without needing to know Tree-sitter internals.
"""

from .models import FunctionNode


def extract_functions(tree) -> list[FunctionNode]:
    """
    Walk the AST and return a list of FunctionNode objects representing
    every function/procedure defined in the source file.
    """
    # TODO: implement AST walk
    raise NotImplementedError
