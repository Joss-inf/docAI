"""API.md generator — detailed function and class signatures."""

from __future__ import annotations
from src.semantic.ir_schema import ProjectIR, FileIR
from src.graph.call_graph import CallGraph

def generate_api_doc(project: ProjectIR, call_graph: CallGraph = None) -> str:
    """Generate a full API reference from IR signatures."""
    lines = [f"# API Reference — {project.project_name}", ""]

    for file_ir in sorted(project.files, key=lambda f: f.file_path):
        if not file_ir.functions and not file_ir.classes:
            continue
            
        lines.append(f"## `{file_ir.file_path}`")
        lines.append(f"**Role**: {file_ir.role.value}")
        lines.append("")

        for func in file_ir.functions:
            lines.append(_render_function(func))
        
        for cls in file_ir.classes:
            lines.append(f"### Class `{cls.name}`")
            if cls.docstring: lines.append(f"> {cls.docstring[:300]}")
            lines.append("")
            for method in cls.methods:
                lines.append(_render_function(method, indent="####"))
        
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def _render_function(func, indent: str = "###") -> str:
    params = ", ".join(f"`{p.name}: {p.type_hint}`" if p.type_hint else f"`{p.name}`" for p in func.params)
    ret = f" → `{func.return_type}`" if func.return_type else ""
    async_tag = " ⚡" if func.is_async else ""
    
    parts = [f"{indent} `{func.name}({params})`{ret}{async_tag}"]
    if func.docstring:
        parts.append(f"> {func.docstring[:300]}")
    if func.calls:
        parts.append(f"**Calls**: `{', '.join(func.calls[:10])}`")
    parts.append("")
    return "\n".join(parts)
