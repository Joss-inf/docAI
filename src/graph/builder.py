"""Builds a NetworkX DiGraph from the project IR imports."""

from __future__ import annotations
import logging
from pathlib import PurePosixPath
import networkx as nx
from src.semantic.ir_schema import FileIR, ProjectIR

logger = logging.getLogger(__name__)


def build_dependency_graph(project: ProjectIR) -> nx.DiGraph:
    """Create a directed graph where edges represent import relationships.

    Nodes are file paths (relative).  An edge A → B means "A imports B".
    """
    graph = nx.DiGraph()

    # Register every file as a node
    file_lookup = _build_file_lookup(project)
    for file_ir in project.files:
        graph.add_node(file_ir.file_path, role=file_ir.role.value)

    # Resolve imports to edges
    for file_ir in project.files:
        for imp in file_ir.imports:
            target = _resolve_import(imp.module, file_ir.file_path, file_lookup)
            if target and target != file_ir.file_path:
                graph.add_edge(file_ir.file_path, target)
                logger.debug("Edge: %s → %s", file_ir.file_path, target)
            elif imp.module and not imp.module.startswith(("os", "sys", "re", "json")):
                logger.debug("Unresolved import: %s in %s", imp.module, file_ir.file_path)

    return graph


def _build_file_lookup(project: ProjectIR) -> dict[str, str]:
    """Map possible module names to their file paths."""
    lookup: dict[str, str] = {}
    for file_ir in project.files:
        path = PurePosixPath(file_ir.file_path)
        # "src/config" → "src.config.py"
        module_key = str(path.with_suffix("")).replace("/", ".")
        lookup[module_key] = file_ir.file_path
        # Also register the basename without extension
        lookup[path.stem] = file_ir.file_path
    return lookup


def _resolve_import(module: str, source_file: str, lookup: dict[str, str]) -> str | None:
    """Try to resolve an import string to a known project file."""
    # Direct match
    if module in lookup:
        return lookup[module]

    # Try partial match (e.g. "config" matching "codedocai.config")
    for key, path in lookup.items():
        if key.endswith(f".{module}") or key == module:
            return path

    return None
