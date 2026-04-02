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

_NOISE_CALLS = {
    "print", "len", "str", "int", "bool", "float", "list", "dict", "set", "tuple", "range", 
    "zip", "enumerate", "isinstance", "issubclass", "hasattr", "getattr", "setattr", "delattr", 
    "super", "type", "id", "hash", "dir", "vars", "locals", "globals", "open", "input", 
    "append", "extend", "pop", "remove", "insert", "clear", "index", "count", "sort", 
    "reverse", "copy", "update", "keys", "values", "items", "get", "setdefault", "add", 
    "discard", "union", "intersection", "difference", "symmetric_difference", "issubset", 
    "issuperset", "isdisjoint", "format", "join", "split", "replace", "strip", "lstrip", "rstrip",
    "lower", "upper", "capitalize", "title", "swapcase", "startswith", "endswith", "find", 
    "rfind", "index", "rindex", "count", "encode", "decode", "zfill", "center", "ljust", "rjust",
    "map", "filter", "reduce", "max", "min", "sum", "any", "all", "round", "abs", "divmod", "pow",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError", "AttributeError", "Exception",
    "getLogger", "info", "debug", "warning", "error", "exception", "logger", "self", "cls"
}

_NOISE_PREFIXES = [
    "click.", "logging.", "pathlib.", "os.path.", "shutil.", "ast.", "re.", "json.", "inspect.", "typing."
]

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


def _scrub_noise_calls(func: FunctionIR) -> None:
    """Filter out standard library, built-in, and framework noise from the function calls."""
    cleaned = []
    for call in func.calls:
        base_term = call.split(".")[-1]
        if base_term in _NOISE_CALLS or call in _NOISE_CALLS:
            continue
            
        if any(call.startswith(prefix) for prefix in _NOISE_PREFIXES):
            continue
            
        if call.startswith("self.") or call.startswith("cls."):
            continue

        cleaned.append(call)
    func.calls = cleaned


def enrich_file_ir(file_ir: FileIR) -> FileIR:
    """Enrich a FileIR with roles, side-effects, criticality, and data flow."""
    file_ir.role = _detect_role(file_ir)
    for func in file_ir.functions:
        _scrub_noise_calls(func)
        func.side_effects = _detect_side_effects(func)
        _enrich_data_flow(func)
    for cls in file_ir.classes:
        for method in cls.methods:
            _scrub_noise_calls(method)
            method.side_effects = _detect_side_effects(method)
            _enrich_data_flow(method)
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


# ── Data Flow heuristics ────────────────────────────────────────────
_READ_PATTERNS = ["open", "read", "get", "select", "fetch"]
_WRITE_PATTERNS = ["open", "write", "save", "insert", "update", "delete", "post", "put"]
_IO_PATTERNS = _READ_PATTERNS + _WRITE_PATTERNS + ["requests.", "httpx.", "socket", "db."]
_NETWORK_PATTERNS = ["requests.", "httpx.", "urllib", "fetch", "axios", "socket"]
_DB_PATTERNS = ["cursor.", "execute", "session.", "query", "sql", ".commit"]


def _enrich_data_flow(func: FunctionIR) -> None:
    """Enrich function with inferred reads, writes, and side-effect flags."""
    call_text = " ".join(func.calls).lower()

    # Track reads/writes
    func.reads = [kw for kw in _READ_PATTERNS if kw in call_text]
    func.writes = [kw for kw in _WRITE_PATTERNS if kw in call_text]
    func.io_operations = [kw for kw in _IO_PATTERNS if kw in call_text]

    # Deduplicate
    func.reads = list(dict.fromkeys(func.reads))
    func.writes = list(dict.fromkeys(func.writes))
    func.io_operations = list(dict.fromkeys(func.io_operations))

    # Explicit behavior flags
    func.mutates_state = bool(func.writes)
    func.has_io = bool(func.io_operations)
    func.network_access = any(kw in call_text for kw in _NETWORK_PATTERNS)
    func.db_access = any(kw in call_text for kw in _DB_PATTERNS)

    # Side-effect weight → importance
    weight = len(func.writes) * 2 + len(func.io_operations) * 3
    if weight > 5:
        func.criticality = "HIGH"
    elif weight > 1:
        func.criticality = "MEDIUM"
    else:
        func.criticality = "LOW"

    # Remove legacy attributes
    if hasattr(func, "purity"):
        delattr(func, "purity")
    if hasattr(func, "side_effect_weight"):
        delattr(func, "side_effect_weight")