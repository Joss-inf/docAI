"""Cycle detection using Tarjan's SCC algorithm via NetworkX."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import networkx as nx

from codedocai.graph.call_graph import CallGraph

logger = logging.getLogger(__name__)


@dataclass
class CycleWarning:
    """A detected cycle with analysis of its impact and fixes."""
    cycle_path: list[str]
    type: Literal["import", "call"]
    severity: Literal["low", "medium", "high"]
    explanation: str
    fix_suggestion: str


@dataclass
class CycleReport:
    """Result of cycle detection in the dependency graph."""
    has_cycles: bool = False
    cycles: list[CycleWarning] = field(default_factory=list)


def detect_cycles(graph: nx.DiGraph, call_graph: CallGraph) -> CycleReport:
    """Find all strongly connected components in imports and calls."""
    report = CycleReport()

    # 1. File Import Cycles
    file_sccs = list(nx.strongly_connected_components(graph))
    for scc in file_sccs:
        if len(scc) > 1:
            cycle_path = sorted(scc)
            report.cycles.append(
                CycleWarning(
                    cycle_path=cycle_path,
                    type="import",
                    severity="low",
                    explanation="Modules depend on each other at the top level.",
                    fix_suggestion="Use lazy imports inside functions or split into a third shared module."
                )
            )
            report.has_cycles = True
            logger.warning("Import cycle detected: %s", " → ".join(cycle_path))

    # 2. Function Call Recursion Cycles
    call_sccs = list(nx.strongly_connected_components(call_graph.nx_graph))
    for scc in call_sccs:
        if len(scc) > 1:
            # Check if this spans multiple files or just local recursion
            cycle_path = sorted(scc)
            files_involved = {node.split("::")[0] for node in cycle_path}
            
            if len(files_involved) > 1:
                sev = "high"
                exp = "Cross-file recursive call loop. This can cause stack overflows and tight coupling."
                fix = "Refactor the logic to avoid mutually recursive calls across boundaries."
            else:
                sev = "medium"
                exp = "Local recursive call loop. Typical for recursive algorithms."
                fix = "Ensure standard base-case exits are implemented."

            report.cycles.append(
                CycleWarning(
                    cycle_path=cycle_path,
                    type="call",
                    severity=sev,
                    explanation=exp,
                    fix_suggestion=fix
                )
            )
            report.has_cycles = True
            logger.warning("Call cycle detected: %s", " → ".join(cycle_path))

    return report
