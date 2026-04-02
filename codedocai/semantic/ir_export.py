"""IR export — persist and reload ProjectIR for caching and debugging."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from codedocai.semantic.ir_schema import ProjectIR

logger = logging.getLogger(__name__)


def export_ir(project: ProjectIR, output_dir: Path) -> Path:
    """Write the full ProjectIR to a JSON file for debugging / RAG use."""
    output_path = output_dir / "ir_dump.json"
    data = project.model_dump(mode="json")
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("IR exported to %s", output_path)
    return output_path


def load_ir(output_dir: Path) -> ProjectIR | None:
    """Load a previously exported ProjectIR, if available."""
    ir_path = output_dir / "ir_dump.json"
    if not ir_path.exists():
        return None
    try:
        data = json.loads(ir_path.read_text(encoding="utf-8"))
        return ProjectIR.model_validate(data)
    except Exception as exc:
        logger.warning("Failed to load cached IR: %s", exc)
        return None


def file_hash(file_path: Path) -> str:
    """Compute a SHA-256 hash for a file's contents."""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()
