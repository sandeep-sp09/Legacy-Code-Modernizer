"""
Unit tests for the dependency graph module.
Run with: pytest tests/test_dependency_graph.py -v
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parser.models import FunctionNode, VariableNode, CallNode
from dependency_graph.graph_builder import build_call_graph, get_graph_context
from dependency_graph.graph_export import to_json


@pytest.fixture
def sample_functions():
    """Create sample FunctionNode objects mimicking the Pascal sample."""
    add_fn = FunctionNode(
        name="AddNumbers",
        parameters=[VariableNode("a", "integer"), VariableNode("b", "integer")],
        local_variables=[],
        calls=[],
        start_line=5,
        end_line=8,
        language="pascal",
    )
    main_fn = FunctionNode(
        name="__main__",
        parameters=[],
        local_variables=[VariableNode("x", "integer"), VariableNode("y", "integer"), VariableNode("sum", "integer")],
        calls=[CallNode("AddNumbers", 13), CallNode("writeln", 14)],
        start_line=10,
        end_line=15,
        language="pascal",
    )
    return [add_fn, main_fn]


class TestBuildCallGraph:
    def test_nodes_created(self, sample_functions):
        graph = build_call_graph(sample_functions)
        assert "AddNumbers" in graph.nodes
        assert "__main__" in graph.nodes

    def test_edges_created(self, sample_functions):
        graph = build_call_graph(sample_functions)
        assert graph.has_edge("__main__", "AddNumbers")
        assert graph.has_edge("__main__", "writeln")

    def test_no_reverse_edge(self, sample_functions):
        graph = build_call_graph(sample_functions)
        assert not graph.has_edge("AddNumbers", "__main__")

    def test_node_metadata(self, sample_functions):
        graph = build_call_graph(sample_functions)
        data = graph.nodes["AddNumbers"]
        assert data["parameters"] == ["a", "b"]
        assert data["language"] == "pascal"
        assert data["start_line"] == 5

    def test_edge_count(self, sample_functions):
        graph = build_call_graph(sample_functions)
        # __main__ -> AddNumbers, __main__ -> writeln
        assert graph.number_of_edges() == 2


class TestGetGraphContext:
    def test_context_for_leaf_function(self, sample_functions):
        graph = build_call_graph(sample_functions)
        ctx = get_graph_context(graph, "AddNumbers")
        assert "Called by:" in ctx
        assert "__main__" in ctx
        assert "Calls:" in ctx

    def test_context_for_main(self, sample_functions):
        graph = build_call_graph(sample_functions)
        ctx = get_graph_context(graph, "__main__")
        assert "AddNumbers" in ctx
        assert "writeln" in ctx

    def test_context_for_unknown(self, sample_functions):
        graph = build_call_graph(sample_functions)
        ctx = get_graph_context(graph, "nonexistent")
        assert "not in the call graph" in ctx


class TestGraphExport:
    def test_to_json(self, sample_functions):
        graph = build_call_graph(sample_functions)
        json_str = to_json(graph)
        assert "AddNumbers" in json_str
        assert "__main__" in json_str

    def test_json_parseable(self, sample_functions):
        import json
        graph = build_call_graph(sample_functions)
        json_str = to_json(graph)
        data = json.loads(json_str)
        assert "nodes" in data or "links" in data  # node-link format
