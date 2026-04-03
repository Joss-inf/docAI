"""Python AST parser — uses the built-in `ast` module (zero external deps)."""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from src.parser.base_parser import AbstractParser
from src.semantic.ir_schema import (
    ClassIR,
    FileIR,
    FunctionIR,
    ImportIR,
    Language,
    ParameterIR,
)

logger = logging.getLogger(__name__)


class PythonParser(AbstractParser):
    """Extracts IR from Python source files using the stdlib `ast` module."""

    def parse(self, file_path: Path, relative_path: str) -> FileIR:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as exc:
            logger.warning("Syntax error in %s: %s", relative_path, exc)
            return FileIR(file_path=relative_path, language=Language.PYTHON)

        return FileIR(
            file_path=relative_path,
            language=Language.PYTHON,
            module_docstring=ast.get_docstring(tree),
            imports=self._extract_imports(tree),
            functions=self._extract_functions(tree),
            classes=self._extract_classes(tree),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_imports(self, tree: ast.Module) -> list[ImportIR]:
        imports: list[ImportIR] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportIR(module=alias.name, alias=alias.asname))
            elif isinstance(node, ast.ImportFrom):
                imports.append(
                    ImportIR(
                        module=node.module or "",
                        names=[a.name for a in node.names],
                        is_relative=node.level > 0,
                    )
                )
        return imports

    def _extract_functions(self, tree: ast.Module) -> list[FunctionIR]:
        """Extract top-level functions (not methods inside classes)."""
        return [
            self._build_function_ir(node)
            for node in ast.iter_child_nodes(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    def _extract_classes(self, tree: ast.Module) -> list[ClassIR]:
        classes: list[ClassIR] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    self._build_function_ir(m)
                    for m in node.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                classes.append(
                    ClassIR(
                        name=node.name,
                        bases=[self._unparse_node(b) for b in node.bases],
                        docstring=ast.get_docstring(node),
                        methods=methods,
                        decorators=[self._unparse_node(d) for d in node.decorator_list],
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                    )
                )
        return classes

    def _build_function_ir(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionIR:
        params = self._extract_params(node.args)
        return_type = self._unparse_node(node.returns) if node.returns else None
        calls = self._extract_calls(node)

        return FunctionIR(
            name=node.name,
            params=params,
            return_type=return_type,
            decorators=[self._unparse_node(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
            calls=calls,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
        )

    def _extract_params(self, args: ast.arguments) -> list[ParameterIR]:
        params: list[ParameterIR] = []
        for arg in args.args:
            if arg.arg == "self":
                continue
            params.append(
                ParameterIR(
                    name=arg.arg,
                    type_hint=self._unparse_node(arg.annotation) if arg.annotation else None,
                )
            )
        return params

    def _extract_calls(self, node: ast.AST) -> list[str]:
        """Collect names of all function/method calls inside a node."""
        calls: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                calls.append(self._unparse_node(child.func))
        return calls

    @staticmethod
    def _unparse_node(node: ast.AST | None) -> str:
        """Safely convert an AST node back to its source string."""
        if node is None:
            return ""
        try:
            return ast.unparse(node)
        except Exception:
            return "<unknown>"
