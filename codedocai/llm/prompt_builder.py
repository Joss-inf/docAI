"""Prompt builder — constructs LLM prompts from IR data only.

CRITICAL POLICY: No raw source code is ever sent to the LLM.
Only structured IR metadata (signatures, types, roles, calls).
"""

from __future__ import annotations

from codedocai.semantic.ir_schema import FileIR, ProjectIR


def build_file_summary_prompt(file_ir: FileIR) -> str:
    """Build a prompt for summarizing a single file from its IR."""
    lines = [
        f"Summarize the following source file based on its structure.",
        f"File: {file_ir.file_path}",
        f"Language: {file_ir.language.value}",
        f"Role: {file_ir.role.value}",
        "",
    ]

    if file_ir.module_docstring:
        lines.append(f"Module docstring: {file_ir.module_docstring}")
        lines.append("")

    if file_ir.imports:
        lines.append("Imports:")
        for imp in file_ir.imports:
            names = ", ".join(imp.names) if imp.names else imp.module
            lines.append(f"  - {imp.module}: {names}")
        lines.append("")

    if file_ir.functions:
        lines.append("Functions:")
        for func in file_ir.functions:
            sig = _format_function_sig(func)
            lines.append(f"  - {sig}")
            if func.docstring:
                lines.append(f"    Docstring: {func.docstring[:200]}")
            if func.calls:
                lines.append(f"    Calls: {', '.join(func.calls[:10])}")
        lines.append("")

    if file_ir.classes:
        lines.append("Classes:")
        for cls in file_ir.classes:
            bases = f" extends {', '.join(cls.bases)}" if cls.bases else ""
            lines.append(f"  - {cls.name}{bases}")
            if cls.docstring:
                lines.append(f"    Docstring: {cls.docstring[:200]}")
            for method in cls.methods:
                lines.append(f"    - {_format_function_sig(method)}")
        lines.append("")

    lines.append("Write a 2-3 sentence summary describing what this file does and its role in the project.")
    return "\n".join(lines)


def build_project_summary_prompt(project: ProjectIR, file_summaries: dict[str, str]) -> str:
    """Build a prompt for the project-level summary using file summaries."""
    lines = [
        f"Summarize the following software project.",
        f"Project: {project.project_name}",
        f"Total files: {len(project.files)}",
        "",
        "File summaries:",
    ]
    for path, summary in file_summaries.items():
        lines.append(f"  - {path}: {summary}")

    lines.append("")
    lines.append("Write a concise project overview (3-5 sentences) covering purpose, architecture, and key components.")
    return "\n".join(lines)


def _format_function_sig(func) -> str:
    """Format a function signature from its IR."""
    params = ", ".join(
        f"{p.name}: {p.type_hint}" if p.type_hint else p.name
        for p in func.params
    )
    ret = f" -> {func.return_type}" if func.return_type else ""
    async_prefix = "async " if func.is_async else ""
    return f"{async_prefix}{func.name}({params}){ret}"
