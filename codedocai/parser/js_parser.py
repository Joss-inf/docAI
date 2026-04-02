"""JavaScript/TypeScript parser — regex-based lightweight extraction.

For the MVP, we use a regex + heuristic approach to avoid requiring
tree-sitter C compilation on Windows.  A tree-sitter backend can be
swapped in later without changing the IR output.
"""

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
_IMPORT_RE = re.compile(
    r"""(?:import\s+(?P<default>\w+)\s+from\s+['"](?P<mod1>[^'"]+)['"]"""
    r"""|import\s*\{(?P<names>[^}]+)\}\s*from\s*['"](?P<mod2>[^'"]+)['"]"""
    r"""|(?:const|let|var)\s+(?:\w+|\{[^}]+\})\s*=\s*require\(['"](?P<mod3>[^'"]+)['"]\))""",
    re.MULTILINE,
)

_FUNCTION_RE = re.compile(
    r"""(?:export\s+)?(?:(?P<async>async)\s+)?function\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)""",
    re.MULTILINE,
)

_ARROW_RE = re.compile(
    r"""(?:export\s+)?(?:const|let|var)\s+(?P<name>\w+)\s*=\s*(?P<async>async\s+)?\((?P<params>[^)]*)\)\s*(?::\s*(?P<ret>[^=>{]+))?\s*=>""",
    re.MULTILINE,
)

_CLASS_RE = re.compile(
    r"""(?:export\s+)?class\s+(?P<name>\w+)(?:\s+extends\s+(?P<base>\w+))?""",
    re.MULTILINE,
)

_METHOD_RE = re.compile(
    r"""(?:(?P<async>async)\s+)?(?P<name>\w+)\s*\((?P<params>[^)]*)\)""",
)


class JSParser(AbstractParser):
    """Lightweight JS/TS parser using regex patterns."""

    def parse(self, file_path: Path, relative_path: str) -> FileIR:
        lang = Language.TYPESCRIPT if file_path.suffix in (".ts", ".tsx") else Language.JAVASCRIPT
        source = file_path.read_text(encoding="utf-8", errors="replace")

        return FileIR(
            file_path=relative_path,
            language=lang,
            imports=self._extract_imports(source),
            functions=self._extract_functions(source),
            classes=self._extract_classes(source),
        )

    def _extract_imports(self, source: str) -> list[ImportIR]:
        imports: list[ImportIR] = []
        for m in _IMPORT_RE.finditer(source):
            module = m.group("mod1") or m.group("mod2") or m.group("mod3") or ""
            names_str = m.group("names") or ""
            names = [n.strip() for n in names_str.split(",") if n.strip()]
            default = m.group("default")
            if default:
                names.insert(0, default)
            imports.append(ImportIR(module=module, names=names))
        return imports

    def _extract_functions(self, source: str) -> list[FunctionIR]:
        funcs: list[FunctionIR] = []
        for m in _FUNCTION_RE.finditer(source):
            funcs.append(self._match_to_func(m))
        for m in _ARROW_RE.finditer(source):
            funcs.append(self._match_to_func(m))
        return funcs

    def _extract_classes(self, source: str) -> list[ClassIR]:
        classes: list[ClassIR] = []
        for m in _CLASS_RE.finditer(source):
            name = m.group("name")
            base = m.group("base")
            classes.append(
                ClassIR(
                    name=name,
                    bases=[base] if base else [],
                    line_start=source[: m.start()].count("\n") + 1,
                )
            )
        return classes

    @staticmethod
    def _match_to_func(m: re.Match) -> FunctionIR:
        raw_params = m.group("params") or ""
        params = [
            ParameterIR(name=p.split(":")[0].strip(), type_hint=p.split(":")[1].strip() if ":" in p else None)
            for p in raw_params.split(",")
            if p.strip()
        ]
        raw_ret = m.groupdict().get("ret")
        return FunctionIR(
            name=m.group("name"),
            params=params,
            is_async=bool(m.group("async")),
            return_type=raw_ret.strip() if raw_ret else None,
            line_start=0,
        )
