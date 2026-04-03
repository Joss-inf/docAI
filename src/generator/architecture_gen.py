"""ARCHITECTURE.md generator — structural overview and dependency analysis."""

from __future__ import annotations
import networkx as nx
from src.generator.mermaid_gen import generate_dependency_diagram
from src.semantic.ir_schema import ProjectIR
from src.semantic.entry_points import EntryPoint

def generate_architecture_doc(project: ProjectIR, graph: nx.DiGraph, file_summaries: dict[str, str], entry_points: list[EntryPoint] = None) -> str:
    """Generate ARCHITECTURE.md with dependency diagrams and project topology."""
    lines = [
        f"# Architecture Overview — {project.project_name}",
        "",
        "## Dependency Graph",
        "This diagram shows how modules import each other. Core engine layers are at the bottom.",
        "",
        generate_dependency_diagram(graph),
        "",
        "## Core Components",
        "Overview of the project structure and module roles.",
        ""
    ]

    for file_ir in sorted(project.files, key=lambda f: f.file_path):
        summary = file_summaries.get(file_ir.file_path, "No summary available.")
        role_label = _role_icon(file_ir.role.value)
        lines.append(f"- {role_label} **`{file_ir.file_path}`** — {summary}")

    if entry_points:
        lines.extend([
            "",
            "## Entry Points",
            "Identified executable roots and their reachability.",
            "| Entry Point | Type | Reachable Functions | Depth |",
            "|-------------|------|---------------------|-------|",
        ])
        for ep in entry_points:
            lines.append(f"| `{ep.function_id}` | {ep.type} | {len(ep.reachable_functions)} | {ep.execution_depth} |")

    return "\n".join(lines)

def _role_icon(role: str) -> str:
    icons = {
        "controller": "🎮 [CTRL]",
        "service": "⚙️ [SERV]",
        "repository": "🗄️ [REPO]",
        "model": "📦 [MODEL]",
        "utility": "🔧 [UTIL]",
        "config": "⚙️ [CONF]",
        "test": "🧪 [TEST]",
        "generic": "📄 [FILE]",
    }
    return icons.get(role, "📄 [FILE]")
