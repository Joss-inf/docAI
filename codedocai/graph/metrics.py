"""Graph metrics — centrality, criticality scoring, and topological sort."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import networkx as nx

from codedocai.graph.call_graph import CallGraph
from codedocai.semantic.ir_schema import ProjectIR

logger = logging.getLogger(__name__)


@dataclass
class NodeMetrics:
    """Metrics for a single file module in the dependency graph."""
    file_path: str
    in_degree: int
    out_degree: int
    fan_out: int
    call_depth: int
    side_effect_weight: int
    criticality: float


def compute_metrics(graph: nx.DiGraph, call_graph: CallGraph, project: ProjectIR) -> list[NodeMetrics]:
    """Compute V2 Criticality by blending structural file deps with functional execution bounds."""
    # Precompute call graph metrics
    cg_metrics = call_graph.compute_metrics()

    # Aggregate function metrics by file
    file_func_metrics = {}
    for file_ir in project.files:
        path = file_ir.file_path
        f_out = 0
        depth = 0
        se_w = 0
        
        # Functions
        for func in file_ir.functions:
            se_w += (1 if func.mutates_state else 0) + (1 if func.has_io else 0) + (2 if func.network_access else 0) + (2 if func.db_access else 0)
            node_id = f"{path}::{func.name}"
            if m := cg_metrics.get(node_id):
                f_out += m["fan_out"]
                depth = max(depth, m["call_depth"])
                
        # Classes
        for cls in file_ir.classes:
            for method in cls.methods:
                se_w += (1 if method.mutates_state else 0) + (1 if method.has_io else 0) + (2 if method.network_access else 0) + (2 if method.db_access else 0)
                node_id = f"{path}::{cls.name}::{method.name}"
                if m := cg_metrics.get(node_id):
                    f_out += m["fan_out"]
                    depth = max(depth, m["call_depth"])
                    
        file_func_metrics[path] = {"fan_out": f_out, "call_depth": depth, "side_effect_weight": se_w}

    metrics: list[NodeMetrics] = []
    
    for file_path in graph.nodes:
        in_deg = graph.in_degree(file_path)
        out_deg = graph.out_degree(file_path)
        
        fm = file_func_metrics.get(file_path, {"fan_out": 0, "call_depth": 0, "side_effect_weight": 0})
        fan_out = fm["fan_out"]
        call_depth = fm["call_depth"]
        side_effect_weight = fm["side_effect_weight"]

        # V2 Criticality formula
        criticality = float(in_deg + out_deg + fan_out + call_depth + side_effect_weight)
        
        metrics.append(
            NodeMetrics(
                file_path=file_path,
                in_degree=in_deg,
                out_degree=out_deg,
                fan_out=fan_out,
                call_depth=call_depth,
                side_effect_weight=side_effect_weight,
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
