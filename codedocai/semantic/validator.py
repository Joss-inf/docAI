"""IR validator — checks schema completeness and flags ambiguities."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from codedocai.semantic.ir_schema import FileIR, ProjectIR

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Outcome of validating a ProjectIR."""
    is_valid: bool = True
    warnings: list[str] = field(default_factory=list)
    ambiguous_symbols: list[str] = field(default_factory=list)


def validate_project_ir(project: ProjectIR) -> ValidationResult:
    """Validate the entire project IR for completeness and consistency."""
    result = ValidationResult()

    # Track all defined symbols for uniqueness check
    symbol_counts: dict[str, int] = {}

    for file_ir in project.files:
        _validate_file(file_ir, result)

        for func in file_ir.functions:
            _count_symbol(symbol_counts, func.name)
        for cls in file_ir.classes:
            _count_symbol(symbol_counts, cls.name)

    # Flag ambiguous (duplicate) symbol names
    for name, count in symbol_counts.items():
        if count > 1:
            result.ambiguous_symbols.append(f"[[Ambiguous]] {name} (defined {count} times)")
            result.warnings.append(f"Symbol '{name}' defined {count} times across files")
            logger.warning("Ambiguous symbol: %s (%d definitions)", name, count)

    if result.warnings:
        result.is_valid = False

    return result


def _validate_file(file_ir: FileIR, result: ValidationResult) -> None:
    """Check a single file IR for issues."""
    if not file_ir.functions and not file_ir.classes:
        result.warnings.append(f"{file_ir.file_path}: no functions or classes extracted")

    for func in file_ir.functions:
        if not func.name:
            result.warnings.append(f"{file_ir.file_path}: function with empty name")


def _count_symbol(counts: dict[str, int], name: str) -> None:
    counts[name] = counts.get(name, 0) + 1
