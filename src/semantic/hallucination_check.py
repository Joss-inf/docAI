"""Hallucination shield — cross-checks LLM summaries against IR data."""

from __future__ import annotations
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
from src.semantic.ir_schema import FileIR, FunctionIR, ClassIR

logger = logging.getLogger(__name__)

class HallucinationSeverity(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class HallucinationReport:
    file_path: str
    severity: HallucinationSeverity = HallucinationSeverity.NONE
    flagged_terms: List[str] = field(default_factory=list)
    missing_critical: List[str] = field(default_factory=list)
    wrong_relationships: List[str] = field(default_factory=list)
    fabricated_behavior: List[str] = field(default_factory=list)
    score: float = 0.0
    total_terms_checked: int = 0
    confidence: float = 0.0

def build_symbol_whitelist(file_ir: FileIR) -> set[str]:
    terms = {file_ir.file_path, file_ir.language.value, file_ir.role.value}
    for imp in file_ir.imports:
        terms.add(imp.module)
        terms.update(imp.names)
    for f in file_ir.functions:
        terms.add(f.name)
        terms.update(f.calls)
        for p in f.params: terms.add(p.name)
    for c in file_ir.classes:
        terms.add(c.name)
        for m in c.methods:
            terms.add(m.name)
            terms.update(m.calls)
            for p in m.params: terms.add(p.name)
    return {t for t in terms if t and len(str(t)) > 2}

def check_summary(file_ir: FileIR, summary: str) -> HallucinationReport:
    report = HallucinationReport(file_path=file_ir.file_path)
    whitelist = build_symbol_whitelist(file_ir)
    
    # Technical terms extraction
    terms = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{3,}\b", summary)
    report.total_terms_checked = len(terms)
    
    stop_words = {"the", "this", "that", "using", "uses", "file", "module", "project", "code", "data", "them", "with", "and", "for"}
    
    for t in terms:
        if t.lower() in stop_words: continue
        # Fuzzy match or direct check
        valid = any(t.lower() in str(w).lower() for w in whitelist)
        if not valid:
            report.flagged_terms.append(t)

    report.score = len(report.flagged_terms) / max(1, len(terms))
    if report.score > 0.5: report.severity = HallucinationSeverity.HIGH
    elif report.score > 0: report.severity = HallucinationSeverity.LOW
    
    _check_missing_critical_components(file_ir, summary, report, None)
    return report

def _check_missing_critical_components(file_ir, summary, report, config):
    summary_l = summary.lower()
    for f in file_ir.functions:
        if f.criticality == "HIGH" and f.name.lower() not in summary_l:
            report.missing_critical.append(f.name)