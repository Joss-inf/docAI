"""Mermaid diagram generator."""

import networkx as nx

def generate_dependency_diagram(graph: nx.DiGraph) -> str:
    """Render a Mermaid flowchart from the dependency graph."""
    lines = ["```mermaid", "flowchart TD"]
    
    # Simple node and edge collection
    for node in graph.nodes:
        # Sanitize name for Mermaid
        clean_node = node.replace("/", "_").replace(".", "_")
        lines.append(f"    {clean_node}[\"{node}\"]")
    
    for u, v in graph.edges:
        clean_u = u.replace("/", "_").replace(".", "_")
        clean_v = v.replace("/", "_").replace(".", "_")
        lines.append(f"    {clean_u} --> {clean_v}")
    
    lines.append("```")
    return "\n".join(lines)
