"""
Builds a NetworkX dependency graph from the parser module's extracted
FunctionNode IR objects.
"""

import networkx as nx


def build_call_graph(functions: list) -> "nx.DiGraph":
    """
    Args:
        functions: list of parser.models.FunctionNode

    Returns:
        networkx.DiGraph where nodes are function names and edges represent
        "calls" relationships (A -> B means A calls B).
    """
    graph = nx.DiGraph()

    for fn in functions:
        graph.add_node(fn.name)

    for fn in functions:
        for call in fn.calls:
            graph.add_edge(fn.name, call.callee_name)

    return graph
