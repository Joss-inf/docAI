"""Entry point detection — identifying where the application starts executing."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import networkx as nx

from codedocai.graph.call_graph import CallGraph
from codedocai.semantic.ir_schema import ModuleRole, ProjectIR

logger = logging.getLogger(__name__)


@dataclass
class EntryPoint:
    """An execution root node inside the application."""
    file_path: str
    function_id: str
    type: Literal["CLI", "MAIN", "API", "WORKER", "UNKNOWN"]
    reachable_functions: list[str] = field(default_factory=list)
    execution_depth: int = 0


def detect_entry_points(project: ProjectIR, call_graph: CallGraph) -> list[EntryPoint]:
    """Scan the project for executable roots and trace their execution trees."""
    entry_points: list[EntryPoint] = []

    # 1. Identify entry roots based on heuristics
    for file_ir in project.files:
        for func in file_ir.functions:
            ep_type: str | None = None
            node_id = f"{file_ir.file_path}::{func.name}"

            # CLI triggers (click, argparse)
            if "@click.command" in func.decorators or "@click.group" in func.decorators:
                ep_type = "CLI"
            # Main functions or rust `pub fn main`
            elif func.name == "main":
                ep_type = "MAIN"
            # API handlers (FastAPI, Flask, Axum routers usually marked by controller roles)
            elif file_ir.role == ModuleRole.CONTROLLER and (
                "get" in func.decorators or "post" in func.decorators or "route" in func.decorators
            ):
                ep_type = "API"

            if ep_type:
                logger.debug("Found entry point: %s (Type: %s)", node_id, ep_type)
                ep = EntryPoint(
                    file_path=file_ir.file_path,
                    function_id=node_id,
                    type=ep_type,  # type: ignore
                )
                entry_points.append(ep)

        # Class based endpoints
        for cls in file_ir.classes:
            for method in cls.methods:
                node_id = f"{file_ir.file_path}::{cls.name}::{method.name}"
                if file_ir.role == ModuleRole.CONTROLLER and (
                    "get" in method.decorators or "post" in method.decorators or "route" in method.decorators
                ):
                    ep = EntryPoint(
                        file_path=file_ir.file_path,
                        function_id=node_id,
                        type="API",
                    )
                    entry_points.append(ep)

    # 2. Traverse Call Graph to build reachable trees
    for ep in entry_points:
        if ep.function_id in call_graph.nodes:
            # DFS reachable nodes from this entry point
            reachable = nx.descendants(call_graph.nx_graph, ep.function_id)
            ep.reachable_functions = list(reachable)

            # Execution depth (max tree depth)
            paths = nx.single_source_shortest_path_length(call_graph.nx_graph, ep.function_id)
            ep.execution_depth = max(paths.values()) if paths else 0

    logger.info("Detected %d entry points.", len(entry_points))
    return entry_points
