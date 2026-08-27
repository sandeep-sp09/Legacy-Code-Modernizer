"""
Helpers to export a NetworkX graph for visualization or for the frontend to consume.
"""

import json
import networkx as nx


def to_json(graph: "nx.DiGraph") -> str:
    """Export graph as node-link JSON, consumable by the frontend."""
    data = nx.node_link_data(graph)
    return json.dumps(data, indent=2)


def to_png(graph: "nx.DiGraph", output_path: str) -> None:
    """Render the graph to a PNG file using matplotlib."""
    import matplotlib.pyplot as plt

    nx.draw(graph, with_labels=True, node_color="lightblue", node_size=1500, font_size=8)
    plt.savefig(output_path)
    plt.close()
