"""Base parser classes and factory."""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from src.semantic.ir_schema import FileIR


class AbstractParser(ABC):
    @abstractmethod
    def parse(self, path: Path, relative_path: str) -> FileIR:
        """Parse a source file and return its IR."""
        pass


def get_parser(language: str) -> AbstractParser:
    """Factory: return the right parser for a language string."""
    from src.parser.python_parser import PythonParser
    from src.parser.js_parser import JSParser
    from src.parser.rust_parser import RustParser

    _registry: dict[str, AbstractParser] = {
        "python": PythonParser(),
        "javascript": JSParser(),
        "typescript": JSParser(),
        "rust": RustParser(),
    }
    parser = _registry.get(language)
    if parser is None:
        raise ValueError(f"No parser available for language: {language}")
    return parser
