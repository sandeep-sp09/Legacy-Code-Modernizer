"""
Parser module — Tree-sitter based AST extraction from Pascal/C source code.

Usage:
    from parser import parse_source, extract_functions
    from parser.models import FunctionNode, VariableNode, CallNode

    tree, lang = parse_source("samples/pascal/sample1.pas")
    functions = extract_functions(tree, lang, source_code)
"""

from .ast_builder import parse_source, load_source
from .ast_extractor import extract_functions
from .models import FunctionNode, VariableNode, CallNode, ControlFlowNode

__all__ = [
    "parse_source",
    "load_source",
    "extract_functions",
    "FunctionNode",
    "VariableNode",
    "CallNode",
    "ControlFlowNode",
]
