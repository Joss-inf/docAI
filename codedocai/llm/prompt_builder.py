"""Prompt builder — constructs LLM prompts merging structured IR and full raw source code."""

from __future__ import annotations

from codedocai.semantic.ir_schema import FileIR, ProjectIR
from codedocai.semantic.entry_points import EntryPoint
from codedocai.graph.metrics import NodeMetrics

# ── Format instructions appended to every prompt ────────────────────
_FORMAT_RULES = """
RULES:
- Provide ONLY a factual behavioral description of what this code does.
- Focus strictly on real mechanics: functions called, data read/written, and side effects.
- Do NOT use JUDGMENTAL labels like "High Criticality", "Important", or "Essential".
- Do NOT use internal formatting markers like [WHO], [WHAT], [HOW].
- Do NOT use markdown code blocks or formatting (bold, italics) in your output.
- Do NOT start with "Okay", "Sure", or any preamble.
- GROUNDING: Mention ONLY identifiers from the Provided Whitelist/IR.
- LEAK PREVENTION: Do NOT include instructions, whitelists, or internal metadata in your final response.
- If multiple files are provided, format as: [FILE: path] Summary...
/no_think
"""


def build_file_summary_prompt(
    file_ir: FileIR,
    source_code: str,
    whitelist: set[str],
    incoming_calls: list[str] | None = None,
    imported_by: list[str] | None = None,
    imports_from: list[str] | None = None,
) -> str:
    """Build a prompt for summarizing a single file from its IR.

    Includes cross-file dependency context when available.
    """
    lines = [
        f"Summarize this source file based on its structure.",
        f"File: {file_ir.file_path}",
        f"Language: {file_ir.language.value}",
        f"Role: {file_ir.role.value}",
        "",
    ]

    # Cross-file context
    if imported_by:
        lines.append(f"Imported by: {', '.join(imported_by[:5])}")
    if imports_from:
        lines.append(f"Depends on: {', '.join(imports_from[:5])}")
    if imported_by or imports_from:
        lines.append("")

    if file_ir.module_docstring:
        lines.append(f"Module docstring: {file_ir.module_docstring[:300]}")
        lines.append("")

    if file_ir.imports:
        lines.append("Imports:")
        for imp in file_ir.imports[:10]:
            names = ", ".join(imp.names) if imp.names else imp.module
            lines.append(f"  - {imp.module}: {names}")
        lines.append("")

    if file_ir.functions:
        lines.append("Functions:")
        for func in file_ir.functions:
            sig = _format_function_sig(func)
            lines.append(f"  - {sig}")
            if func.docstring:
                lines.append(f"    Docstring: {func.docstring[:150]}")
            if func.calls:
                lines.append(f"    Calls: {', '.join(func.calls[:8])}")
        lines.append("")

    if file_ir.classes:
        lines.append("Classes:")
        for cls in file_ir.classes:
            bases = f" extends {', '.join(cls.bases)}" if cls.bases else ""
            lines.append(f"  - {cls.name}{bases}")
            if cls.docstring:
                lines.append(f"    Docstring: {cls.docstring[:150]}")
            for method in cls.methods[:10]:
                lines.append(f"    - {_format_function_sig(method)}")
        lines.append("")

    lines.append("SYMBOL WHITELIST (Allowed terminology):")
    lines.append(f"  {', '.join(sorted(whitelist))}")
    lines.append("")

    if incoming_calls:
        lines.append("INCOMING CALLS (Who uses this file):")
        lines.append(f"  {', '.join(incoming_calls[:10])}")
        lines.append("")

    if source_code:
        lines.append("SOURCE CODE:")
        lines.append("```")
        lines.append(source_code)
        lines.append("```")
    else:
        lines.append("(Note: Full source code omitted for brevity. Summarize based ONLY on the structured IR provided above.)")
        
    lines.append("")
    lines.append(_FORMAT_RULES)
    return "\n".join(lines)


def build_project_summary_prompt(
    project: ProjectIR, 
    file_summaries: dict[str, str],
    entry_points: list[EntryPoint] | None = None,
    metrics: list[NodeMetrics] | None = None,
) -> str:
    """Build a prompt for the project-level summary using file summaries."""
    lines = [
        f"Summarize this software project.",
        f"Project: {project.project_name}",
        f"Total files: {len(project.files)}",
        "",
        "File summaries:",
    ]
    for path, summary in list(file_summaries.items())[:20]:
        lines.append(f"  - {path}: {summary[:120]}")

    lines.append("")
    
    if entry_points:
        lines.append("Execution Entry Points:")
        for ep in entry_points:
            lines.append(f"  - [{ep.type.upper()}] {ep.function_id} -> reaches {len(ep.reachable_functions)} functions")
        lines.append("")

    if metrics:
        lines.append("Top Critical Modules (Execution Core):")
        for m in metrics[:5]:
            lines.append(f"  - {m.file_path} (Criticality Score: {m.criticality:.1f})")
        lines.append("")

    lines.append("Write a concise project overview (3-5 sentences) describing the ACTUAL execution pipeline. Start by explaining how execution begins at the Entry Points, and how data physically routes through the Top Critical Modules. Do NOT generate generic folder breakdowns or list files.")
    lines.append(_FORMAT_RULES)
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


def build_batch_summary_prompt(
    batch: list[tuple[FileIR, set[str]]],
) -> str:
    """Build a prompt for summarizing multiple files at once."""
    lines = ["Summarize the following source files based on their structured IR.", ""]
    
    for file_ir, whitelist in batch:
        lines.append(f"--- FILE: {file_ir.file_path} ---")
        lines.append(f"Language: {file_ir.language.value}")
        lines.append(f"Role: {file_ir.role.value}")
        
        if file_ir.functions:
            lines.append("Functions:")
            for func in file_ir.functions:
                lines.append(f"  - {_format_function_sig(func)}")
                if func.calls:
                    lines.append(f"    Calls: {', '.join(func.calls[:5])}")
                    
        if file_ir.classes:
            lines.append("Classes:")
            for cls in file_ir.classes:
                lines.append(f"  - {cls.name}")
        
        lines.append(f"ALLOWED TERMS: {', '.join(sorted(whitelist))}")
        lines.append("")

    lines.append("Output your response as a valid JSON object where keys are the file paths and values are the 1-2 sentence factual summaries.")
    lines.append("Example: { \"file/path.py\": \"Summary...\" }")
    lines.append(_FORMAT_RULES)
    return "\n".join(lines)
