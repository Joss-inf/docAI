"""Fallback templates — generate deterministic summaries when LLM is unavailable."""

from __future__ import annotations
from src.semantic.ir_schema import FileIR


def generate_fallback_summary(file_ir: FileIR) -> str:
    """Produce a template-based summary from IR when LLM fails."""
    parts = [f"**{file_ir.file_path}** ({file_ir.language.value}, role: {file_ir.role.value})"]

    func_count = len(file_ir.functions)
    class_count = len(file_ir.classes)

    if class_count:
        class_names = ", ".join(c.name for c in file_ir.classes)
        parts.append(f"Defines {class_count} class(es): {class_names}.")

    if func_count:
        func_names = ", ".join(f.name for f in file_ir.functions)
        parts.append(f"Contains {func_count} function(s): {func_names}.")

    if file_ir.imports:
        deps = ", ".join(sorted({i.module for i in file_ir.imports if i.module}))
        parts.append(f"Depends on: {deps}.")

    if file_ir.module_docstring:
        parts.append(f"Description: {file_ir.module_docstring[:300]}")

    return " ".join(parts)


def generate_fallback_project_summary(file_summaries: dict[str, str]) -> str:
    """Produce a template-based project summary when LLM fails."""
    total = len(file_summaries)
    return (
        f"This project contains {total} source file(s). "
        "See individual file summaries below for details."
    )
