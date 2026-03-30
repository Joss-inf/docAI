"""Cycle detection using Tarjan's SCC algorithm via NetworkX."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class CycleReport:
    """Result of cycle detection in the dependency graph."""
    has_cycles: bool = False
    cycles: list[list[str]] = field(default_factory=list)


def detect_cycles(graph: nx.DiGraph) -> CycleReport:
    """Find all strongly connected components with more than one node (cycles)."""
    report = CycleReport()

    sccs = list(nx.strongly_connected_components(graph))
    for scc in sccs:
        if len(scc) > 1:
            cycle_path = sorted(scc)
            report.cycles.append(cycle_path)
            report.has_cycles = True
            logger.warning("Circular dependency detected: %s", " → ".join(cycle_path))

    return report
