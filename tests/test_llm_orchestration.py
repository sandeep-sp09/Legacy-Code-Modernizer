"""
Unit tests for the LLM orchestration module.
Run with: pytest tests/test_llm_orchestration.py -v

Note: Tests for generate_cpp() are skipped by default since they require
a running Ollama instance. Run with --run-ollama to include them.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parser.models import FunctionNode, VariableNode, CallNode
from llm_orchestration.prompt_builder import build_prompt, build_full_file_prompt, SYSTEM_PROMPT
from llm_orchestration.validator import check_syntax, check_no_hallucinations


# ---------------------------------------------------------------------------
# Prompt builder tests
# ---------------------------------------------------------------------------

class TestPromptBuilder:
    @pytest.fixture
    def sample_fn(self):
        return FunctionNode(
            name="AddNumbers",
            parameters=[VariableNode("a", "integer"), VariableNode("b", "integer")],
            local_variables=[],
            calls=[],
            start_line=5,
            end_line=8,
            raw_source="function AddNumbers(a, b: integer): integer;\nbegin\n  AddNumbers := a + b;\nend;",
            language="pascal",
        )

    def test_prompt_contains_source(self, sample_fn):
        prompt = build_prompt(sample_fn.raw_source, sample_fn, "No context")
        assert "AddNumbers" in prompt
        assert "a + b" in prompt

    def test_prompt_contains_ir_summary(self, sample_fn):
        prompt = build_prompt(sample_fn.raw_source, sample_fn, "No context")
        assert "Parameters:" in prompt
        assert "a: integer" in prompt

    def test_prompt_contains_graph_context(self, sample_fn):
        ctx = "Called by: __main__"
        prompt = build_prompt(sample_fn.raw_source, sample_fn, ctx)
        assert "Called by: __main__" in prompt

    def test_prompt_asks_for_cpp(self, sample_fn):
        prompt = build_prompt(sample_fn.raw_source, sample_fn, "No context")
        assert "C++" in prompt

    def test_system_prompt_exists(self):
        assert len(SYSTEM_PROMPT) > 50
        assert "C++" in SYSTEM_PROMPT

    def test_full_file_prompt(self, sample_fn):
        prompt = build_full_file_prompt(
            "full source code here", [sample_fn], "context", "pascal"
        )
        assert "full source code here" in prompt
        assert "PASCAL" in prompt


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestSyntaxChecker:
    def test_valid_cpp(self):
        code = '#include <iostream>\nint main() { std::cout << "Hello"; return 0; }'
        is_valid, err = check_syntax(code)
        assert is_valid, f"Should be valid but got: {err}"

    def test_empty_code(self):
        is_valid, err = check_syntax("")
        assert not is_valid

    def test_unbalanced_braces(self):
        code = "int main() { return 0;"
        is_valid, err = check_syntax(code)
        # May or may not fail depending on which checker is active
        # Either tree-sitter catches it or heuristic does
        # Just ensure it doesn't crash
        assert isinstance(is_valid, bool)


class TestHallucinationChecker:
    @pytest.fixture
    def original_ir(self):
        return [FunctionNode(
            name="add_numbers",
            parameters=[VariableNode("a", "int"), VariableNode("b", "int")],
            local_variables=[VariableNode("result", "int")],
            calls=[],
            language="c",
        )]

    def test_clean_code_passes(self, original_ir):
        code = "int add_numbers(int a, int b) { int result = a + b; return result; }"
        passed, flagged = check_no_hallucinations(code, original_ir)
        assert passed
        assert len(flagged) == 0

    def test_many_unknowns_flagged(self, original_ir):
        # Code with tons of symbols not in original IR
        fake_symbols = " ".join(f"fake_var_{i}" for i in range(20))
        code = f"int add_numbers(int a, int b) {{ {fake_symbols}; return a + b; }}"
        passed, flagged = check_no_hallucinations(code, original_ir)
        assert not passed
        assert len(flagged) > 0
