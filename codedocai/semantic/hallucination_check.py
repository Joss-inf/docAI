"""Hallucination shield — cross-checks LLM summaries against IR data."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from codedocai.semantic.ir_schema import FileIR

logger = logging.getLogger(__name__)


@dataclass
class HallucinationReport:
    """Result of cross-checking a summary against its IR."""
    file_path: str
    score: float = 0.0  # 0.0 = clean, 1.0 = fully hallucinated
    flagged_terms: list[str] = field(default_factory=list)
    total_terms_checked: int = 0


def build_symbol_whitelist(file_ir: FileIR) -> set[str]:
    """Collect all valid identifiers from the IR for grounding."""
    return _build_all_known_terms(file_ir)


def check_summary(file_ir: FileIR, summary: str) -> HallucinationReport:
    """Cross-check an LLM summary against the file's IR.

    Extracts technical terms from the summary and verifies each
    one exists somewhere in the IR (function names, class names,
    import modules, param names, etc.).
    """
    report = HallucinationReport(file_path=file_ir.file_path)

    # Build a set of all known terms from IR
    known_terms = _build_all_known_terms(file_ir)

    # Extract technical terms from the summary (CamelCase, snake_case, dotted)
    summary_terms = _extract_technical_terms(summary)
    report.total_terms_checked = len(summary_terms)

    if not summary_terms:
        return report

    for term in summary_terms:
        term_lower = term.lower()
        # Check if the term matches any known IR term
        if not any(term_lower in known.lower() or known.lower() in term_lower for known in known_terms):
            report.flagged_terms.append(term)

    report.score = len(report.flagged_terms) / len(summary_terms) if summary_terms else 0.0

    if report.flagged_terms:
        logger.debug(
            "Hallucination check %s: %.0f%% (flagged: %s)",
            file_ir.file_path,
            report.score * 100,
            ", ".join(report.flagged_terms[:5]),
        )

    return report


def _build_all_known_terms(file_ir: FileIR) -> set[str]:
    """Collect all identifiers from the IR."""
    terms: set[str] = set()

    # File path parts
    terms.update(file_ir.file_path.replace("/", " ").replace("\\", " ").replace(".", " ").split())

    # Language and role
    terms.add(file_ir.language.value)
    terms.add(file_ir.role.value)

    # Imports
    for imp in file_ir.imports:
        terms.add(imp.module)
        terms.update(imp.names)

    # Functions
    for func in file_ir.functions:
        terms.add(func.name)
        terms.update(p.name for p in func.params)
        terms.update(func.calls)
        if func.return_type:
            terms.add(func.return_type)

    # Classes
    for cls in file_ir.classes:
        terms.add(cls.name)
        terms.update(cls.bases)
        for method in cls.methods:
            terms.add(method.name)
            terms.update(p.name for p in method.params)

    # Remove empty strings and very short terms
    return {t for t in terms if len(t) > 2}


def _extract_technical_terms(text: str) -> list[str]:
    """Extract likely technical identifiers from a text summary."""
    # Match: CamelCase, camelCase, snake_case, kebab-case, dot.notation, ALL_CAPS
    pattern = r'\b[a-z]+[A-Z][a-zA-Z0-9]+\b|\b[A-Z][a-zA-Z0-9]+(?:[A-Z][a-z]+)*\b|\b\w+(?:[_-]\w+)+\b|\b\w+\.\w+\b'
    matches = re.findall(pattern, text)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    stop_words = {"The", "This", "That", "Any", "For", "What", "When", "How", "Why", "Are", "Will", "Can"}
    for m in matches:
        if m not in seen and m not in stop_words and len(m) > 3:
            seen.add(m)
            unique.append(m)
    return unique
