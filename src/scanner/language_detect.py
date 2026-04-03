"""Maps file extensions to a canonical language identifier."""

from __future__ import annotations

from enum import Enum
from pathlib import Path


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    UNKNOWN = "unknown"


# Extension → Language lookup (lowercase, with dot)
_EXT_MAP: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".pyw": Language.PYTHON,
    ".js": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    ".mjs": Language.JAVASCRIPT,
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TYPESCRIPT,
    ".rs": Language.RUST,
}


def detect_language(file_path: Path) -> Language:
    """Return the language for a given file path based on its extension."""
    return _EXT_MAP.get(file_path.suffix.lower(), Language.UNKNOWN)
