"""Cycle detection for dependency graphs."""

from __future__ import annotations
from dataclasses import dataclass, field
import networkx as nx
from src.graph.call_graph import CallGraph

@dataclass
class SingleCycle:
    cycle_path: list[str]

@dataclass
class CycleReport:
    has_cycles: bool = False
    cycles: list[SingleCycle] = field(default_factory=list)

def detect_cycles(graph: nx.DiGraph, call_graph: CallGraph = None) -> CycleReport:
    """Detect circular dependencies using NetworkX."""
    try:
        cycles_raw = list(nx.simple_cycles(graph))
        cycles = [SingleCycle(cycle_path=c) for c in cycles_raw]
        return CycleReport(has_cycles=len(cycles) > 0, cycles=cycles)
    except Exception:
        return CycleReport()
