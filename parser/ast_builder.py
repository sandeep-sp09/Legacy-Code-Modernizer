"""
Builds a raw Tree-sitter AST from Pascal/C source code.

Uses individual grammar packages (tree-sitter-c, tree-sitter-pascal) instead
of tree-sitter-languages, which is incompatible with Python 3.14.
"""

from pathlib import Path
from tree_sitter import Language, Parser

import tree_sitter_c
import tree_sitter_pascal

# Pre-build Language objects once at module load
_LANGUAGES = {
    "c": Language(tree_sitter_c.language()),
    "pascal": Language(tree_sitter_pascal.language()),
}

# Map file extensions to language names
_EXT_MAP = {
    ".c": "c",
    ".h": "c",
    ".pas": "pascal",
    ".pp": "pascal",
    ".dpr": "pascal",
    ".lpr": "pascal",
}


def _detect_language(file_path: str) -> str:
    """Detect language from file extension."""
    ext = Path(file_path).suffix.lower()
    lang = _EXT_MAP.get(ext)
    if lang is None:
        raise ValueError(
            f"Cannot detect language for extension '{ext}'. "
            f"Supported: {list(_EXT_MAP.keys())}"
        )
    return lang


def parse_source(file_path: str, language: str | None = None):
    """
    Parse a source file and return the raw Tree-sitter tree.

    Args:
        file_path: path to the .pas or .c file to parse.
        language: "pascal" or "c". If None, auto-detected from extension.

    Returns:
        tuple[tree_sitter.Tree, str]: (parsed tree, detected language name)
    """
    if language is None:
        language = _detect_language(file_path)

    language = language.lower()
    if language not in _LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported: {list(_LANGUAGES.keys())}"
        )

    source = load_source(file_path)
    lang_obj = _LANGUAGES[language]
    parser = Parser(lang_obj)
    tree = parser.parse(source.encode("utf-8"))
    return tree, language


def load_source(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")
