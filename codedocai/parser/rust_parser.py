"""Rust parser — lightweight regex-based extraction for Rust source files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from codedocai.parser.base_parser import AbstractParser
from codedocai.semantic.ir_schema import (
    ClassIR,
    FileIR,
    FunctionIR,
    ImportIR,
    Language,
    ParameterIR,
)

logger = logging.getLogger(__name__)

# ── Regex patterns ──────────────────────────────────────────────────
_USE_RE = re.compile(
    r"""use\s+(?P<path>[\w:]+)(?:::(?:\{(?P<names>[^}]+)\}|\*))?;""",
    re.MULTILINE,
)

_FN_RE = re.compile(
    r"""(?:pub\s+)?(?:(?P<async>async)\s+)?fn\s+(?P<name>\w+)\s*(?:<[^>]*>)?\s*\((?P<params>[^)]*)\)(?:\s*->\s*(?P<ret>[^{]+?))??\s*\{""",
    re.MULTILINE,
)

_STRUCT_RE = re.compile(
    r"""(?:pub\s+)?struct\s+(?P<name>\w+)""",
    re.MULTILINE,
)

_IMPL_RE = re.compile(
    r"""impl(?:\s*<[^>]*>)?\s+(?P<name>\w+)""",
    re.MULTILINE,
)

_MOD_RE = re.compile(r"""mod\s+(?P<name>\w+)\s*;""", re.MULTILINE)


class RustParser(AbstractParser):
    """Lightweight Rust parser using regex patterns."""

    def parse(self, file_path: Path, relative_path: str) -> FileIR:
        source = file_path.read_text(encoding="utf-8", errors="replace")

        structs = self._extract_structs(source)
        funcs = self._extract_functions(source)
        
        # Remove functions that were claimed as struct methods
        method_names = {m.name for s in structs for m in s.methods}
        top_funcs = [f for f in funcs if f.name not in method_names]

        return FileIR(
            file_path=relative_path,
            language=Language.RUST,
            imports=self._extract_imports(source),
            functions=top_funcs,
            classes=structs,
        )

    def _extract_imports(self, source: str) -> list[ImportIR]:
        imports: list[ImportIR] = []
        for m in _USE_RE.finditer(source):
            path = m.group("path")
            names_str = m.group("names") or ""
            names = [n.strip() for n in names_str.split(",") if n.strip()]
            imports.append(ImportIR(module=path, names=names))
        for m in _MOD_RE.finditer(source):
            imports.append(ImportIR(module=m.group("name"), names=[]))
        return imports

    def _extract_functions(self, source: str) -> list[FunctionIR]:
        funcs: list[FunctionIR] = []
        for m in _FN_RE.finditer(source):
            raw_params = m.group("params") or ""
            params = self._parse_params(raw_params)
            ret = (m.group("ret") or "").strip() or None
            is_async = bool(m.group("async"))
            funcs.append(
                FunctionIR(
                    name=m.group("name"),
                    params=params,
                    return_type=ret,
                    is_async=is_async,
                    line_start=source[: m.start()].count("\n") + 1,
                )
            )
        return funcs

    def _extract_structs(self, source: str) -> list[ClassIR]:
        """Map Rust structs to ClassIR for unified representation."""
        structs: list[ClassIR] = []
        struct_names = set()
        for m in _STRUCT_RE.finditer(source):
            name = m.group("name")
            struct_names.add(name)
            structs.append(
                ClassIR(
                    name=name,
                    line_start=source[: m.start()].count("\n") + 1,
                )
            )

        # Attach impl methods to their structs
        for m in _IMPL_RE.finditer(source):
            impl_name = m.group("name")
            for s in structs:
                if s.name == impl_name:
                    impl_start = m.end()
                    depth = 0
                    in_block = False
                    impl_end = impl_start
                    for i in range(impl_start, len(source)):
                        if source[i] == '{':
                            depth += 1
                            in_block = True
                        elif source[i] == '}':
                            depth -= 1
                        if in_block and depth == 0:
                            impl_end = i
                            break
                    
                    impl_source = source[impl_start:impl_end]
                    for fn_m in _FN_RE.finditer(impl_source):
                        raw_params = fn_m.group("params") or ""
                        params = self._parse_params(raw_params)
                        s.methods.append(
                            FunctionIR(
                                name=fn_m.group("name"),
                                params=params,
                                return_type=(fn_m.group("ret") or "").strip() or None,
                            )
                        )
                    break

        return structs

    @staticmethod
    def _parse_params(raw: str) -> list[ParameterIR]:
        params: list[ParameterIR] = []
        for part in raw.split(","):
            part = part.strip()
            if not part or part in ("&self", "&mut self", "self"):
                continue
            if ":" in part:
                name, type_hint = part.split(":", 1)
                params.append(ParameterIR(name=name.strip(), type_hint=type_hint.strip()))
            else:
                params.append(ParameterIR(name=part))
        return params
