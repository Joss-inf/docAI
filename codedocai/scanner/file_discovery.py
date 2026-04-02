"""Recursive file discovery with .gitignore support."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pathspec

from codedocai.scanner.language_detect import Language, detect_language

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscoveredFile:
    """A source file discovered during scanning."""
    path: Path
    relative_path: str
    language: Language
    size_bytes: int


def _load_gitignore(project_root: Path) -> pathspec.PathSpec | None:
    """Load .gitignore patterns from the project root."""
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return None
    with open(gitignore, "r", encoding="utf-8", errors="ignore") as f:
        return pathspec.PathSpec.from_lines("gitwildmatch", f)


def discover_files(
    project_root: Path,
    supported_extensions: list[str],
    exclude_dirs: list[str],
) -> Iterator[DiscoveredFile]:
    """Walk the project tree and yield source files, respecting .gitignore."""
    project_root = project_root.resolve()
    gitignore_spec = _load_gitignore(project_root)
    exclude_set = {d.lower() for d in exclude_dirs}

    for file_path in project_root.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip excluded directories
        if any(part.lower() in exclude_set for part in file_path.relative_to(project_root).parts):
            continue

        # Skip extensions we don't support
        if file_path.suffix.lower() not in supported_extensions:
            continue

        relative = file_path.relative_to(project_root).as_posix()

        # Hard-ignore boilerplate indexers
        if file_path.name in {"__init__.py", "index.js", "index.ts", "mod.rs"}:
            continue

        # Respect .gitignore
        if gitignore_spec and gitignore_spec.match_file(relative):
            continue

        language = detect_language(file_path)
        if language == Language.UNKNOWN:
            continue

        logger.debug("Discovered: %s (%s)", relative, language.value)
        yield DiscoveredFile(
            path=file_path,
            relative_path=relative,
            language=language,
            size_bytes=file_path.stat().st_size,
        )
