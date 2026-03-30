"""Semantic enricher — assigns roles, side-effects, and criticality labels."""

from __future__ import annotations

import logging
import re

from codedocai.semantic.ir_schema import (
    FileIR,
    FunctionIR,
    ModuleRole,
    SideEffect,
)

logger = logging.getLogger(__name__)

# ── Side-effect detection keywords ──────────────────────────────────
_SIDE_EFFECT_PATTERNS: dict[SideEffect, list[str]] = {
    SideEffect.IO: ["open", "read", "write", "os.path", "pathlib", "shutil", "fs."],
    SideEffect.NETWORK: ["requests.", "httpx.", "urllib", "fetch", "axios", "socket"],
    SideEffect.DATABASE: ["cursor.", "execute", "session.", "query", "sql", ".commit"],
    SideEffect.PROCESS: ["subprocess", "os.system", "exec", "spawn"],
}

# ── Role heuristics ─────────────────────────────────────────────────
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
    """Enrich a FileIR with roles, side-effects, and criticality."""
    file_ir.role = _detect_role(file_ir)
    for func in file_ir.functions:
        func.side_effects = _detect_side_effects(func)
    for cls in file_ir.classes:
        for method in cls.methods:
            method.side_effects = _detect_side_effects(method)
    return file_ir


def _detect_role(file_ir: FileIR) -> ModuleRole:
    """Determine the module role from file path + class/decorator names."""
    search_text = file_ir.file_path.lower()

    # Also check class names and decorators
    for cls in file_ir.classes:
        search_text += f" {cls.name.lower()}"
        search_text += " ".join(d.lower() for d in cls.decorators)

    for role, pattern in _ROLE_PATTERNS.items():
        if pattern.search(search_text):
            logger.debug("Role %s detected for %s", role.value, file_ir.file_path)
            return role

    return ModuleRole.GENERIC


def _detect_side_effects(func: FunctionIR) -> list[SideEffect]:
    """Scan call targets for known side-effect patterns."""
    effects: list[SideEffect] = []
    call_text = " ".join(func.calls).lower()

    for effect, keywords in _SIDE_EFFECT_PATTERNS.items():
        if any(kw.lower() in call_text for kw in keywords):
            effects.append(effect)

    return effects if effects else [SideEffect.NONE]
