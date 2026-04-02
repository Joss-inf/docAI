"""ARCHITECTURE.md generator — from graph data and IR."""

from __future__ import annotations

import networkx as nx

from codedocai.generator.mermaid_gen import generate_dependency_diagram, generate_call_graph_diagram
from codedocai.generator.utils import role_icon, sanitize_summary
from codedocai.graph.cycles import CycleReport
from codedocai.graph.metrics import NodeMetrics
from codedocai.semantic.ir_schema import ProjectIR
from codedocai.graph.call_graph import CallGraph
from codedocai.semantic.entry_points import EntryPoint


def generate_architecture_doc(
    project: ProjectIR,
    graph: nx.DiGraph,
    file_summaries: dict[str, str],
    entry_points: list[EntryPoint] = None
) -> str:
    """Generate ARCHITECTURE.md with dependency diagrams, execution flow, and project structure."""
    lines = [f"# Architecture Overview — {project.project_name}", ""]

    # Project summary
    if project.summary:
        lines.append(project.summary)
        lines.append("")

    # Dependency diagram
    lines.append("## Dependency Graph")
    lines.append(generate_dependency_diagram(graph))
    lines.append("")

    # Execution Flow
    if entry_points:
        lines.append("## Execution Flow (Triggers)")
        lines.append("The following execution paths identify the primary entry points and their reachability:")
        lines.append("")
        for ep in entry_points:
            lines.append(f"### {ep.type} Entry: `{ep.function_id}`")
            lines.append(f"- **File**: `{ep.file_path}`")
            lines.append(f"- **Trace Depth**: {ep.execution_depth} calls")
            if ep.reachable_functions:
                lines.append(f"  - _Key Components_: {', '.join(ep.reachable_functions[:5])}")
                if len(ep.reachable_functions) > 5:
                    lines.append(f"  - *(+ {len(ep.reachable_functions) - 5} more)*")
            lines.append("")

    # Project Structure (IR Symbols)
    lines.append("## Project Structure & Internal Components")
    lines.append("Detailed listing of all modules and their exported symbols (Classes/Functions):")
    lines.append("")
    for file_ir in sorted(project.files, key=lambda f: f.file_path):
        summary = file_summaries.get(file_ir.file_path, "")
        summary = sanitize_summary(summary)
        icon = role_icon(file_ir.role.value)
        
        symbols = []
        if file_ir.classes:
            cls_names = [f"`{c.name}`" for c in file_ir.classes]
            symbols.append(f"Classes: {', '.join(cls_names)}")
        if file_ir.functions:
            func_names = [f"`{f.name}`" for f in file_ir.functions if not f.name.startswith('_')]
            if func_names:
                symbols.append(f"Functions: {', '.join(func_names)}")
        
        symbol_text = f" ({' | '.join(symbols)})" if symbols else ""
        lines.append(f"- {icon} **`{file_ir.file_path}`**{symbol_text} — {summary}")
    lines.append("")

    # Project stats
    total_funcs = sum(len(f.functions) for f in project.files)
    total_classes = sum(len(f.classes) for f in project.files)
    lines.append("## Project Stats")
    lines.append(f"- **Total Files**: {len(project.files)}")
    lines.append(f"- **Total Functions**: {total_funcs}")
    lines.append(f"- **Total Classes**: {total_classes}")
    lines.append("")

    return "\n".join(lines)
