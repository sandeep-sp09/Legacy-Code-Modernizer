"""
Dependency graph module — builds and exports call graphs from parser IR.

Usage:
    from dependency_graph import build_call_graph, get_graph_context, to_json, to_png

    graph = build_call_graph(functions)
    context = get_graph_context(graph, "AddNumbers")
    json_str = to_json(graph)
"""

from .graph_builder import build_call_graph, get_graph_context
from .graph_export import to_json, to_png

__all__ = [
    "build_call_graph",
    "get_graph_context",
    "to_json",
    "to_png",
]
