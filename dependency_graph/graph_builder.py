"""
Builds a NetworkX dependency graph from the parser module's extracted
FunctionNode IR objects.
"""

import networkx as nx

from parser.models import FunctionNode


def build_call_graph(functions: list[FunctionNode]) -> nx.DiGraph:
    """
    Args:
        functions: list of parser.models.FunctionNode

    Returns:
        networkx.DiGraph where nodes are function names and edges represent
        "calls" relationships (A -> B means A calls B).
        Each node carries metadata attributes from the FunctionNode.
    """
    graph = nx.DiGraph()

    # Add nodes with metadata
    for fn in functions:
        graph.add_node(
            fn.name,
            parameters=[v.name for v in fn.parameters],
            local_variables=[v.name for v in fn.local_variables],
            start_line=fn.start_line,
            end_line=fn.end_line,
            language=fn.language,
        )

    # Add call edges
    for fn in functions:
        for call in fn.calls:
            graph.add_edge(fn.name, call.callee_name, line=call.line)

    return graph


def get_graph_context(graph: nx.DiGraph, function_name: str) -> str:
    """
    Return a concise text summary of a function's call relationships,
    suitable for inclusion in an LLM prompt.

    Args:
        graph: the call graph built by build_call_graph()
        function_name: the function to describe

    Returns:
        A multi-line string describing callers and callees.
    """
    if function_name not in graph:
        return f"Function '{function_name}' is not in the call graph."

    # Who does this function call?
    callees = list(graph.successors(function_name))
    # Who calls this function?
    callers = list(graph.predecessors(function_name))

    lines = [f"Call context for '{function_name}':"]

    if callers:
        lines.append(f"  Called by: {', '.join(callers)}")
    else:
        lines.append("  Called by: (none / entry point)")

    if callees:
        lines.append(f"  Calls: {', '.join(callees)}")
    else:
        lines.append("  Calls: (none / leaf function)")

    return "\n".join(lines)
