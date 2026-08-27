"""
Builds a raw Tree-sitter AST from Pascal/C source code.
"""

from pathlib import Path


def parse_source(file_path: str, language: str = "pascal"):
    """
    Parse a source file and return the raw Tree-sitter tree.

    Args:
        file_path: path to the .pas or .c file to parse.
        language: "pascal" or "c".

    Returns:
        tree_sitter.Tree
    """
    # TODO: load the appropriate Tree-sitter grammar and parse the file.
    raise NotImplementedError


def load_source(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")
