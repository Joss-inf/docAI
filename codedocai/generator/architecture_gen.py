"""ARCHITECTURE.md generator — from graph data and IR."""

from __future__ import annotations

import networkx as nx

from codedocai.generator.mermaid_gen import generate_dependency_diagram
from codedocai.graph.cycles import CycleReport
from codedocai.graph.metrics import NodeMetrics
from codedocai.semantic.ir_schema import ProjectIR


def generate_architecture_doc(
    project: ProjectIR,
    graph: nx.DiGraph,
    metrics: list[NodeMetrics],
    cycle_report: CycleReport,
) -> str:
    """Generate ARCHITECTURE.md with dependency diagrams and analysis."""
    lines = [f"# Architecture Overview — {project.project_name}", ""]

    # Project summary
    if project.summary:
        lines.append(project.summary)
        lines.append("")

    # Dependency diagram
    lines.append("## Dependency Graph")
    lines.append(generate_dependency_diagram(graph))
    lines.append("")

    # Module criticality table
    lines.append("## Module Criticality")
    lines.append("| File | Role | In-Degree | Out-Degree | Criticality |")
    lines.append("|------|------|-----------|------------|-------------|")
    for m in metrics[:20]:  # Top 20
        role = "—"
        for f in project.files:
            if f.file_path == m.file_path:
                role = f.role.value
                break
        lines.append(f"| `{m.file_path}` | {role} | {m.in_degree} | {m.out_degree} | {m.criticality:.1f} |")
    lines.append("")

    # Cycle warnings
    if cycle_report.has_cycles:
        lines.append("## ⚠️ Circular Dependencies")
        for cycle in cycle_report.cycles:
            lines.append(f"- {' → '.join(cycle)}")
        lines.append("")

    return "\n".join(lines)
