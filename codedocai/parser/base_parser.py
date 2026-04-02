"""Abstract base parser — all language parsers implement this interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from codedocai.semantic.ir_schema import FileIR


class AbstractParser(ABC):
    """Base class for language-specific AST parsers.

    Every parser reads a source file and returns a standardised FileIR.
    """

    @abstractmethod
    def parse(self, file_path: Path, relative_path: str) -> FileIR:
        """Parse a single source file and return its IR."""


def get_parser(language: str) -> AbstractParser:
    """Factory: return the right parser for a language string."""
    from codedocai.parser.python_parser import PythonParser
    from codedocai.parser.js_parser import JSParser
    from codedocai.parser.rust_parser import RustParser

    _registry: dict[str, AbstractParser] = {
        "python": PythonParser(),
        "javascript": JSParser(),
        "typescript": JSParser(),  # same parser handles both
        "rust": RustParser(),
    }
    parser = _registry.get(language)
    if parser is None:
        raise ValueError(f"No parser available for language: {language}")
    return parser
