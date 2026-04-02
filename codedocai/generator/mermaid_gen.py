"""Deterministic Mermaid diagram generation from the dependency graph."""

from __future__ import annotations

import networkx as nx


def generate_dependency_diagram(graph: nx.DiGraph) -> str:
    """Render the project dependency graph as a Mermaid flowchart."""
    lines = ["```mermaid", "graph TD"]

    for node in sorted(graph.nodes):
        safe_id = _sanitize(node)
        lines.append(f'    {safe_id}["{node}"]')

    for source, target in sorted(graph.edges):
        lines.append(f"    {_sanitize(source)} --> {_sanitize(target)}")

    lines.append("```")
    return "\n".join(lines)


def generate_module_diagram(file_ir_list) -> str:
    """Render a class/function overview diagram for a set of files."""
    lines = ["```mermaid", "classDiagram"]

    for file_ir in file_ir_list:
        for cls in file_ir.classes:
            safe_name = cls.name.replace(" ", "_")
            lines.append(f"    class {safe_name} {{")
            for method in cls.methods:
                params = ", ".join(p.name for p in method.params)
                ret = f" {method.return_type}" if method.return_type else ""
                lines.append(f"        +{method.name}({params}){ret}")
            lines.append("    }")

            for base in cls.bases:
                lines.append(f"    {base.replace('.', '_')} <|-- {safe_name}")

    lines.append("```")
    return "\n".join(lines)


def generate_call_graph_diagram(call_graph) -> str:
    """Render the function call execution graph as a Mermaid flowchart (Max 30 top edges)."""
    lines = ["```mermaid", "graph TD"]

    # Filter out external nodes and limit size for rendering
    # We display nodes that have connections or the highest fan-out
    if not call_graph.edges:
        return "*(Call graph is empty)*"

    visible_edges = sorted(call_graph.edges, key=lambda e: e.caller_id + e.callee_id)[:50]
    visible_nodes = set()
    for e in visible_edges:
        visible_nodes.add(e.caller_id)
        visible_nodes.add(e.callee_id)

    for node_id in sorted(visible_nodes):
        node = call_graph.nodes.get(node_id)
        label = node.func_name if node else node_id.split("::")[-1]
        lines.append(f'    {_sanitize(node_id)}["{label}"]')

    for edge in visible_edges:
        lines.append(f"    {_sanitize(edge.caller_id)} --> {_sanitize(edge.callee_id)}")

    lines.append("```")
    return "\n".join(lines)


def _sanitize(name: str) -> str:
    """Convert a file path to a valid Mermaid node ID."""
    return name.replace("/", "_").replace("\\", "_").replace(".", "_").replace("-", "_")
