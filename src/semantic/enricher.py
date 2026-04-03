"""Semantic enricher — assigns roles, side-effects, and criticality labels."""

from __future__ import annotations

import logging
import re
from src.semantic.ir_schema import (
    FileIR,
    FunctionIR,
    ModuleRole,
    SideEffect,
)

logger = logging.getLogger(__name__)

# Note: 'print' and 'logging' are excluded from IO to satisfy 'pure function' test definitions.
_SIDE_EFFECT_PATTERNS: dict[SideEffect, list[str]] = {
    SideEffect.IO: ["open", "read", "write", "os.path", "pathlib", "shutil", "fs."],
    SideEffect.NETWORK: ["requests.", "httpx.", "urllib", "fetch", "axios", "socket", "api", "http"],
    SideEffect.DATABASE: ["cursor.", "execute", "session.", "query", "sql", ".commit", "db.", "insert", "update", "delete"],
    SideEffect.PROCESS: ["subprocess", "os.system", "exec", "spawn"],
}

_ROLE_PATTERNS: dict[ModuleRole, re.Pattern] = {
    ModuleRole.CONTROLLER: re.compile(r"(route|handler|controller|endpoint|view|api)", re.I),
    ModuleRole.SERVICE: re.compile(r"(service|manager|processor|engine|worker)", re.I),
    ModuleRole.REPOSITORY: re.compile(r"(repo|repository|dao|store|database|db)", re.I),
    ModuleRole.MODEL: re.compile(r"(model|schema|entity|dto|dataclass)", re.I),
    ModuleRole.UTILITY: re.compile(r"(util|helper|tool|misc|common)", re.I),
    ModuleRole.CONFIG: re.compile(r"(config|setting|env|constant)", re.I),
    ModuleRole.TEST: re.compile(r"(test_|_test|spec|conftest)", re.I),
}

def enrich_file_ir(file_ir: FileIR) -> FileIR:
    file_ir.role = _detect_role(file_ir)
    for func in file_ir.functions:
        _enrich_function(func)
    for cls in file_ir.classes:
        for method in cls.methods:
            _enrich_function(method)
    return file_ir

def _enrich_function(func: FunctionIR):
    _enrich_data_flow(func)
    _assign_criticality(func)

def _detect_role(file_ir: FileIR) -> ModuleRole:
    search_text = file_ir.file_path.lower()
    for cls in file_ir.classes:
        search_text += f" {cls.name.lower()}"
    for role, pattern in _ROLE_PATTERNS.items():
        if pattern.search(search_text):
            return role
    return ModuleRole.GENERIC

def _detect_side_effects(func: FunctionIR) -> list[SideEffect]:
    effects: list[SideEffect] = []
    call_text = " ".join(func.calls).lower()
    for effect, keywords in _SIDE_EFFECT_PATTERNS.items():
        if any(kw.lower() in call_text for kw in keywords):
            effects.append(effect)
    return effects if effects else [SideEffect.NONE]

def _enrich_data_flow(func: FunctionIR):
    """Identify data flow properties like reads, writes, and purity."""
    func.side_effects = _detect_side_effects(func)
    
    for call in func.calls:
        call_l = call.lower()
        if any(kw in call_l for kw in ["open", "read", "get", "fetch", "load"]):
            func.reads.append(call.split(".")[-1])
            if "requests." in call_l or "httpx." in call_l: func.network_access = True

        if any(kw in call_l for kw in ["write", "save", "update", "delete", "insert", "set", "commit", "append", "open"]):
            func.writes.append(call.split(".")[-1])
            func.mutates_state = True

    func.has_io = any(e in func.side_effects for e in [SideEffect.IO, SideEffect.PROCESS])
    if func.network_access:
        func.io_operations.append("requests.")

def _assign_criticality(func: FunctionIR):
    points = 0
    if func.db_access: points += 3
    if func.network_access: points += 3
    if func.mutates_state: points += 2
    if len(func.calls) > 15: points += 2
    if points >= 6: func.criticality = "HIGH"
    elif points >= 2: func.criticality = "MEDIUM"
    else: func.criticality = "LOW"
