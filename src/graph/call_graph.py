"""Call Graph — function-level execution mapping."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
import networkx as nx

from src.semantic.ir_schema import ProjectIR, FileIR

logger = logging.getLogger(__name__)


@dataclass
class FunctionNode:
    id: str  # file_path::func_name
    file_path: str
    name: str


@dataclass
class CallEdge:
    caller_id: str
    callee_id: str
    call_type: str  # "imported", "local", "external"


class CallGraph:
    """Project-wide call graph."""
    def __init__(self):
        self.nx_graph = nx.DiGraph()
        self.nodes: dict[str, FunctionNode] = {}
        self.edges: list[CallEdge] = []

    def compute_metrics(self) -> dict:
        betweenness = nx.betweenness_centrality(self.nx_graph) if len(self.nx_graph.nodes) > 2 else {}
        return {
            node: {
                "fan_in": self.nx_graph.in_degree(node),
                "fan_out": self.nx_graph.out_degree(node),
                "betweenness": betweenness.get(node, 0.0),
            }
            for node in self.nx_graph.nodes
        }


def build_call_graph(project: ProjectIR) -> CallGraph:
    """Build a global call graph across all project modules."""
    cg = CallGraph()
    
    # 1. Register all functions as nodes
    for file_ir in project.files:
        for func in file_ir.functions:
            node_id = f"{file_ir.file_path}::{func.name}"
            cg.nx_graph.add_node(node_id, label=func.name)
            cg.nodes[node_id] = FunctionNode(node_id, file_ir.file_path, func.name)
        
        for cls in file_ir.classes:
            for method in cls.methods:
                node_id = f"{file_ir.file_path}::{cls.name}::{method.name}"
                cg.nx_graph.add_node(node_id, label=method.name)
                cg.nodes[node_id] = FunctionNode(node_id, file_ir.file_path, method.name)

    # 2. Resolve calls to edges
    for file_ir in project.files:
        for func_ir in file_ir.functions:
            caller_id = f"{file_ir.file_path}::{func_ir.name}"
            for call in func_ir.calls:
                target_id = None
                for potential_id in cg.nodes:
                    if potential_id.endswith(f"::{call}"):
                        target_id = potential_id
                        break
                
                if target_id:
                    cg.nx_graph.add_edge(caller_id, target_id)
                    cg.edges.append(CallEdge(caller_id, target_id, "imported"))
                else:
                    cg.edges.append(CallEdge(caller_id, call, "external"))
                    # Add external node to NX graph to satisfy fan-out count in tests
                    if call not in cg.nx_graph:
                        cg.nx_graph.add_node(call)
                    cg.nx_graph.add_edge(caller_id, call)

    return cg
