"""
Unit tests for the parser module.
Run with: pytest tests/test_parser.py -v
"""

import os
import sys
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parser.ast_builder import parse_source, load_source
from parser.ast_extractor import extract_functions
from parser.models import FunctionNode, VariableNode, CallNode


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")


# ---------------------------------------------------------------------------
# Pascal tests
# ---------------------------------------------------------------------------

class TestPascalParsing:
    """Tests for parsing the Pascal sample file."""

    @pytest.fixture
    def pascal_functions(self):
        path = os.path.join(SAMPLES_DIR, "pascal", "sample1.pas")
        tree, lang = parse_source(path)
        source = load_source(path)
        return extract_functions(tree, lang, source)

    def test_finds_two_functions(self, pascal_functions):
        """Should find AddNumbers function and __main__ block."""
        assert len(pascal_functions) == 2

    def test_addnumbers_function(self, pascal_functions):
        add_fn = pascal_functions[0]
        assert add_fn.name == "AddNumbers"
        assert add_fn.language == "pascal"

    def test_addnumbers_params(self, pascal_functions):
        add_fn = pascal_functions[0]
        param_names = [p.name for p in add_fn.parameters]
        assert "a" in param_names
        assert "b" in param_names
        assert len(add_fn.parameters) == 2

    def test_addnumbers_param_types(self, pascal_functions):
        add_fn = pascal_functions[0]
        for p in add_fn.parameters:
            assert p.var_type == "integer"

    def test_main_block_exists(self, pascal_functions):
        main_fn = pascal_functions[1]
        assert main_fn.name == "__main__"

    def test_main_variables(self, pascal_functions):
        main_fn = pascal_functions[1]
        var_names = [v.name for v in main_fn.local_variables]
        assert "x" in var_names
        assert "y" in var_names
        assert "sum" in var_names

    def test_main_calls(self, pascal_functions):
        main_fn = pascal_functions[1]
        call_names = [c.callee_name for c in main_fn.calls]
        assert "AddNumbers" in call_names
        assert "writeln" in call_names

    def test_line_ranges(self, pascal_functions):
        add_fn = pascal_functions[0]
        assert add_fn.start_line > 0
        assert add_fn.end_line >= add_fn.start_line

    def test_raw_source_populated(self, pascal_functions):
        add_fn = pascal_functions[0]
        assert len(add_fn.raw_source) > 0
        assert "AddNumbers" in add_fn.raw_source


# ---------------------------------------------------------------------------
# C tests
# ---------------------------------------------------------------------------

class TestCParsing:
    """Tests for parsing the C sample file."""

    @pytest.fixture
    def c_functions(self):
        path = os.path.join(SAMPLES_DIR, "c", "sample1.c")
        tree, lang = parse_source(path)
        source = load_source(path)
        return extract_functions(tree, lang, source)

    def test_finds_two_functions(self, c_functions):
        """Should find add_numbers and main."""
        assert len(c_functions) == 2

    def test_add_numbers_function(self, c_functions):
        fn = c_functions[0]
        assert fn.name == "add_numbers"
        assert fn.language == "c"

    def test_add_numbers_params(self, c_functions):
        fn = c_functions[0]
        param_names = [p.name for p in fn.parameters]
        assert "a" in param_names
        assert "b" in param_names
        assert len(fn.parameters) == 2

    def test_add_numbers_param_types(self, c_functions):
        fn = c_functions[0]
        for p in fn.parameters:
            assert p.var_type == "int"

    def test_main_function(self, c_functions):
        fn = c_functions[1]
        assert fn.name == "main"

    def test_main_local_vars(self, c_functions):
        fn = c_functions[1]
        var_names = [v.name for v in fn.local_variables]
        assert "x" in var_names
        assert "y" in var_names
        assert "sum" in var_names

    def test_main_calls(self, c_functions):
        fn = c_functions[1]
        call_names = [c.callee_name for c in fn.calls]
        assert "add_numbers" in call_names
        assert "printf" in call_names

    def test_line_ranges(self, c_functions):
        fn = c_functions[0]
        assert fn.start_line == 3
        assert fn.end_line == 5


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Test error handling and edge cases."""

    def test_auto_detect_pascal(self):
        path = os.path.join(SAMPLES_DIR, "pascal", "sample1.pas")
        tree, lang = parse_source(path)
        assert lang == "pascal"

    def test_auto_detect_c(self):
        path = os.path.join(SAMPLES_DIR, "c", "sample1.c")
        tree, lang = parse_source(path)
        assert lang == "c"

    def test_unsupported_extension(self):
        with pytest.raises(ValueError, match="Cannot detect language"):
            parse_source("test.java")

    def test_unsupported_language(self):
        path = os.path.join(SAMPLES_DIR, "c", "sample1.c")
        with pytest.raises(ValueError, match="Unsupported language"):
            parse_source(path, language="java")
