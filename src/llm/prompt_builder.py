"""Prompt builder — constructs LLM prompts merging structured IR and full raw source code."""

from __future__ import annotations
import json
from src.semantic.ir_schema import FileIR, ProjectIR
from src.graph.metrics import NodeMetrics
from src.semantic.entry_points import EntryPoint

def build_file_summary_prompt(file_ir: FileIR, source_code: str = "", whitelist: set[str] = None, incoming_calls: list[str] = None, imported_by: list[str] = None, imports_from: list[str] = None) -> str:
    """Build a rich grounded prompt for high-fidelity summary."""
    lines = [
        f"Analyze this {file_ir.language.value} module in CodeDocAI.",
        f"Path: {file_ir.file_path}",
        f"Role: {file_ir.role.value}",
        "",
        "## Technical Context",
        f"Dependencies: {len(file_ir.imports)} total.",
        f"Imported by: {', '.join(imported_by[:10]) if imported_by else 'None'}",
        f"Usage context: {', '.join(incoming_calls[:10]) if incoming_calls else 'Internal use only'}",
        "",
        "## Structural Analysis (IR)",
    ]
    
    if file_ir.functions:
        lines.append("Functions:")
        for f in file_ir.functions:
            lines.append(f" - {f.name}({', '.join(p.name for p in f.params)}) -> {f.return_type}")
            if f.calls: lines.append(f"   Internal calls: {', '.join(f.calls[:5])}")

    if file_ir.classes:
        lines.append("\nClasses:")
        for c in file_ir.classes:
            lines.append(f" - {c.name}")
            for m in c.methods:
                lines.append(f"   - {m.name}()")

    if source_code:
        lines.append("\n## Source Code Snippets")
        lines.append(f"```python\n{source_code[:2000]}\n```")

    if whitelist:
        lines.append("\n## Grounding Whitelist")
        lines.append(f"Use ONLY these terms: {', '.join(list(whitelist)[:30])}")

    lines.extend([
        "",
        "TASK: Write a 2-3 sentence technical summary.",
        "RULES:",
        "1. NO SUBJECTIVE language (no 'powerful', 'efficient', 'essential').",
        "2. NO hallucinations. If a module/func isn't in IR/Source, don't mention it.",
        "3. Focus on DATA FLOW and SIDE EFFECTS.",
    ])
    return "\n".join(lines)


def build_batch_summary_prompt(batch_data: list[tuple[FileIR, set[str]]]) -> str:
    """Analyze multiple utility files and return a JSON mapping [path -> summary]."""
    files_info = []
    for f, whitelist in batch_data:
        files_info.append({
            "path": f.file_path,
            "role": f.role.value,
            "functions": [fn.name for fn in f.functions],
            "classes": [c.name for c in f.classes],
            "whitelist": list(whitelist)[:20]
        })

    return f"""Analyze these {len(batch_data)} utility files.
Return a RAW JSON object mapping file paths to 1-sentence technical summaries.
NO PREAMBLE. NO MARKDOWN.

DATA:
{json.dumps(files_info, indent=2)}

FORMAT:
{{
  "path/to/file.py": "Summary of the file."
}}"""


def build_project_summary_prompt(project: ProjectIR, file_summaries: dict[str, str], entry_points: list[EntryPoint] = None, metrics: list[NodeMetrics] = None) -> str:
    """Build a high-level architectural overview prompt."""
    lines = [
        f"Project: {project.project_name}",
        f"Structure: {len(project.files)} modules analyzed.",
        "",
        "## Entry Points"
    ]
    if entry_points:
        for ep in entry_points:
            lines.append(f" - {ep.function_id} ({ep.type})")
            
    lines.append("\n## Core Modules Summary")
    # Top 5 most critical
    if metrics:
        top_critical = sorted(metrics, key=lambda m: m.criticality, reverse=True)[:5]
        for m in top_critical:
            lines.append(f" - {m.file_path}: {file_summaries.get(m.file_path, 'Missing')}")

    lines.extend([
        "",
        "TASK: Write a 4-5 sentence architectural overview for the README.",
        "Describe how data flows from entry points through the core layers.",
    ])
    return "\n".join(lines)
