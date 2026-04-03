"""Rust parser — lightweight regex-based extraction."""

from __future__ import annotations
import re
from pathlib import Path
from src.parser.base_parser import AbstractParser
from src.semantic.ir_schema import FileIR, FunctionIR, ClassIR, ImportIR, ParameterIR, Language


class RustParser(AbstractParser):
    def parse(self, path: Path, relative_path: str) -> FileIR:
        source = path.read_text(encoding="utf-8", errors="replace")
        file_ir = FileIR(file_path=relative_path, language=Language.RUST)
        
        # 1. Imports
        for match in re.finditer(r"use\s+([^;]+);", source):
            file_ir.imports.append(ImportIR(module=match.group(1).strip()))
        for match in re.finditer(r"mod\s+([^;]+);", source):
            file_ir.imports.append(ImportIR(module=match.group(1).strip()))

        # 2. Structs as Classes
        structs: dict[str, ClassIR] = {}
        for match in re.finditer(r"(?:pub\s+)?struct\s+(\w+)", source):
            name = match.group(1)
            cls = ClassIR(name=name)
            structs[name] = cls
            file_ir.classes.append(cls)

        # 3. Impl blocks (methods)
        for match in re.finditer(r"impl\s+(\w+)\s*\{", source):
            struct_name = match.group(1)
            start = match.end()
            depth = 1
            idx = start
            while depth > 0 and idx < len(source):
                if source[idx] == "{": depth += 1
                elif source[idx] == "}": depth -= 1
                idx += 1
            body = source[start:idx-1]
            
            if struct_name in structs:
                cls = structs[struct_name]
                for m_match in re.finditer(r"(async\s+)?(?:pub\s+)?fn\s+(\w+)\s*\(([^)]*)\)\s*(->\s*([^\{]+))?", body):
                    cls.methods.append(self._parse_func_match(m_match))

        # 4. Top-level Functions
        # Match fn or async fn, optional pub
        for match in re.finditer(r"(?:^|\n)(async\s+)?(?:pub\s+)?fn\s+(\w+)\s*\(([^)]*)\)\s*(->\s*([^\{]+))?", source):
            file_ir.functions.append(self._parse_func_match(match))

        return file_ir

    def _parse_func_match(self, match: re.Match) -> FunctionIR:
        is_async = "async" in (match.group(1) or "")
        name = match.group(2)
        params_raw = match.group(3)
        ret = match.group(5).strip() if match.group(5) else None
        
        params = []
        for p in params_raw.split(","):
            if ":" in p:
                parts = p.split(":", 1)
                params.append(ParameterIR(name=parts[0].strip(), type_hint=parts[1].strip()))
        
        return FunctionIR(
            name=name,
            is_async=is_async,
            params=params,
            return_type=ret
        )
