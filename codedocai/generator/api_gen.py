"""API.md generator — deterministic API reference from IR signatures and execution graphs."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from codedocai.graph.call_graph import CallGraph
from codedocai.semantic.ir_schema import FileIR, FunctionIR, ProjectIR

# -------------------------
# Configuration
# -------------------------

DEFAULT_NOISE_CALLS: set[str] = {
    "join", "append", "get", "sorted", "len", "print", "range",
    "enumerate", "isinstance", "getattr", "setattr", "hasattr",
    "is_dir", "exists", "read_text", "write_text",
    "getLogger", "info", "debug", "warning", "error", "exception",
    "click", "logging", "Path", "Pathlib", "shutil", "os", "sys"
}

ROLE_DESCRIPTIONS: dict[str, str] = {
    "config": "Configuration and settings",
    "controller": "Main orchestration logic",
    "generic": "Utility and helper modules",
}

# -------------------------
# Helpers
# -------------------------

def _slugify(text: str) -> str:
    """Convert a string to a valid Markdown anchor."""
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower())
    return slug.strip('-')

def _make_node_id(file_path: str, cls_name: str | None = None, func_name: str | None = None) -> str:
    if cls_name and func_name:
        return f"{file_path}::{cls_name}::{func_name}"
    return f"{file_path}::{func_name}" if func_name else file_path


# -------------------------
# Main generator
# -------------------------

def generate_api_doc(
    project: ProjectIR,
    call_graph: CallGraph,
    include_private: bool = False,
    noise_calls: set[str] | None = None,
    max_flow_calls: int = 5,
) -> str:
    """
    Generate a full API.md from the project IR,
    grouped by module role and enriched with execution insights.
    """
    if noise_calls is None:
        noise_calls = DEFAULT_NOISE_CALLS

    lines = [f"# API Reference — {project.project_name}", ""]

    # Group files by role
    grouped_files = defaultdict(list)
    for file_ir in project.files:
        role = getattr(file_ir, 'role', 'generic')
        grouped_files[role].append(file_ir)

    sorted_roles = sorted(grouped_files.keys())

    # Table of contents
    lines.append("## Table of Contents")
    for role in sorted_roles:
        lines.append(f"- [{role.title()}](#{_slugify(role)})")
        for f in sorted(grouped_files[role], key=lambda f: f.file_path):
            anchor = _slugify(Path(f.file_path).stem)
            lines.append(f"  - [{f.file_path}](#{anchor})")
    lines.append("")

    # Roles
    for role in sorted_roles:
        lines.append(f"## Role: {role.title()}")
        desc = ROLE_DESCRIPTIONS.get(role, "")
        if desc:
            lines.append(f"> {desc}")
        lines.append("")

        for file_ir in sorted(grouped_files[role], key=lambda f: f.file_path):
            section = _render_file_api(
                file_ir,
                call_graph,
                include_private,
                noise_calls,
                max_flow_calls,
            )
            if section:
                lines.append(section)

    return "\n".join(lines)


# -------------------------
# File rendering
# -------------------------

def _render_file_api(
    file_ir: FileIR,
    call_graph: CallGraph,
    include_private: bool,
    noise_calls: set[str],
    max_flow_calls: int,
) -> str:
    """Render the API section for a single file."""
    parts: list[str] = []

    functions = getattr(file_ir, 'functions', [])
    classes = getattr(file_ir, 'classes', [])

    if not functions and not classes:
        return ""

    parts.append(f"### {file_ir.file_path}")
    parts.append(f"**Language**: {file_ir.language.value}")
    parts.append("")

    # Functions
    for func in functions:
        if not include_private and func.name.startswith('_') and not func.name.startswith('__'):
            continue
        parts.append(
            _render_function(
                func,
                file_ir.file_path,
                call_graph,
                noise_calls,
                max_flow_calls,
                indent="####",
            )
        )

    # Classes
    for cls in classes:
        bases = f" ({', '.join(cls.bases)})" if getattr(cls, 'bases', []) else ""
        parts.append(f"#### Class {cls.name}{bases}")

        docstring = getattr(cls, 'docstring', '')
        if docstring:
            parts.append(f"> {docstring[:200]}")

        parts.append("")

        for method in getattr(cls, 'methods', []):
            if not include_private and method.name.startswith('_') and not method.name.startswith('__'):
                continue
            parts.append(
                _render_function(
                    method,
                    file_ir.file_path,
                    call_graph,
                    noise_calls,
                    max_flow_calls,
                    cls_name=cls.name,
                    indent="#####",
                )
            )

    parts.append("---")
    parts.append("")

    return "\n".join(parts)


# -------------------------
# Function rendering
# -------------------------

def _render_function(
    func: FunctionIR,
    file_path: str,
    call_graph: CallGraph,
    noise_calls: set[str],
    max_flow_calls: int,
    cls_name: str | None = None,
    indent: str = "###"
) -> str:
    """Render a single function/method as Markdown."""
    node_id = _make_node_id(file_path, cls_name, func.name)

    params = ", ".join(
        f"{p.name}: {p.type_hint}" if p.type_hint else f"{p.name}"
        for p in getattr(func, 'params', [])
    )

    ret = f" → {func.return_type}" if getattr(func, 'return_type', None) else ""
    async_tag = " ⚡" if getattr(func, 'is_async', False) else ""

    lines = [f"{indent} {func.name}({params}){ret}{async_tag}"]

    docstring = getattr(func, 'docstring', '')
    if docstring:
        lines.append(f"> {docstring[:200]}")

    lines.append("")

    # Call Graph
    callee_edges = [edge for edge in call_graph.edges if edge.caller_id == node_id]

    # Calls (callees)
    if callee_edges:
        lines.append("**Calls:**")
        callees = set()
        for edge in callee_edges:
            callee_name = edge.callee_id.split("::")[-1]
            if not callee_name.startswith(('<', '_')):
                callees.add(callee_name)

        sorted_callees = sorted(callees)
        for name in sorted_callees[:max_flow_calls]:
            lines.append(f"- `{name}`")
        if len(sorted_callees) > max_flow_calls:
            lines.append("- _Other internal calls hidden_")
        lines.append("")

    return "\n".join(lines)