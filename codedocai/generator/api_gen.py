"""API.md generator — deterministic API reference from IR signatures."""

from __future__ import annotations

from codedocai.semantic.ir_schema import FileIR, ProjectIR


def generate_api_doc(project: ProjectIR) -> str:
    """Generate a full API.md from the project IR."""
    lines = [f"# API Reference — {project.project_name}", ""]

    for file_ir in sorted(project.files, key=lambda f: f.file_path):
        section = _render_file_api(file_ir)
        if section:
            lines.append(section)

    return "\n".join(lines)


def _render_file_api(file_ir: FileIR) -> str:
    """Render the API section for a single file."""
    parts: list[str] = []

    if not file_ir.functions and not file_ir.classes:
        return ""

    parts.append(f"## `{file_ir.file_path}`")
    parts.append(f"**Role**: {file_ir.role.value} | **Language**: {file_ir.language.value}")
    parts.append("")

    for func in file_ir.functions:
        parts.append(_render_function(func))

    for cls in file_ir.classes:
        bases = f" ({', '.join(cls.bases)})" if cls.bases else ""
        parts.append(f"### Class `{cls.name}`{bases}")
        if cls.docstring:
            parts.append(f"> {cls.docstring[:200]}")
        parts.append("")
        for method in cls.methods:
            parts.append(_render_function(method, indent="####"))

    parts.append("---")
    parts.append("")
    return "\n".join(parts)


def _render_function(func, indent: str = "###") -> str:
    """Render a single function/method as Markdown."""
    params = ", ".join(
        f"`{p.name}: {p.type_hint}`" if p.type_hint else f"`{p.name}`"
        for p in func.params
    )
    ret = f" → `{func.return_type}`" if func.return_type else ""
    async_tag = " ⚡" if func.is_async else ""

    lines = [f"{indent} `{func.name}({params})`{ret}{async_tag}"]
    if func.docstring:
        lines.append(f"> {func.docstring[:200]}")
    if func.side_effects and func.side_effects[0].value != "none":
        effects = ", ".join(e.value for e in func.side_effects)
        lines.append(f"**Side-effects**: {effects}")
    lines.append("")
    return "\n".join(lines)
