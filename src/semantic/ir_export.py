"""IR export/import utility — handles persistence and caching."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from src.semantic.ir_schema import ProjectIR, FileIR

logger = logging.getLogger(__name__)


def export_ir(project: ProjectIR, output_dir: Path) -> None:
    """Save the project IR to a JSON file for caching and analysis."""
    dump_path = output_dir / "ir_dump.json"
    data = project.model_dump()
    dump_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("IR exported to %s", dump_path)


def load_ir(output_dir: Path) -> ProjectIR | None:
    """Load a previously exported IR from the documentation folder."""
    dump_path = output_dir / "ir_dump.json"
    if not dump_path.exists():
        return None
    try:
        data = json.loads(dump_path.read_text(encoding="utf-8"))
        return ProjectIR.model_validate(data)
    except Exception as e:
        logger.warning("Failed to load cached IR: %s", e)
        return None


def file_hash(path: Path) -> str:
    """Compute a SHA256 hash of a file's content for change detection."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()
