"""Graph metrics — centrality, criticality scoring, and topological sort."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class NodeMetrics:
    """Metrics for a single node in the dependency graph."""
    file_path: str
    in_degree: int
    out_degree: int
    criticality: float


def compute_metrics(graph: nx.DiGraph) -> list[NodeMetrics]:
    """Compute in-degree, out-degree, and criticality for each node."""
    metrics: list[NodeMetrics] = []
    for node in graph.nodes:
        in_deg = graph.in_degree(node)
        out_deg = graph.out_degree(node)
        # Criticality: nodes that are imported by many others are more critical
        criticality = float(in_deg) * 1.0 + float(out_deg) * 0.3
        metrics.append(
            NodeMetrics(
                file_path=node,
                in_degree=in_deg,
                out_degree=out_deg,
                criticality=criticality,
            )
        )
    metrics.sort(key=lambda m: m.criticality, reverse=True)
    return metrics


def topological_order(graph: nx.DiGraph) -> list[str]:
    """Return a deterministic topological ordering of nodes.

    If the graph has cycles, returns best-effort ordering by
    removing back-edges.
    """
    try:
        return list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        logger.warning("Graph has cycles; using lexicographic fallback order")
        return sorted(graph.nodes)
