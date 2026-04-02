"""Call Graph builder — function-level execution mapping."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import networkx as nx

from codedocai.semantic.ir_schema import ProjectIR

logger = logging.getLogger(__name__)


@dataclass
class FunctionNode:
    """A node representing a function or method in the call graph."""
    id: str  # Format: "file_path::[class_name::]func_name"
    file_path: str
    func_name: str
    class_name: str | None = None
    is_async: bool = False


@dataclass
class CallEdge:
    """A directed edge representing a function call."""
    caller_id: str
    callee_id: str
    call_type: Literal["local", "imported", "method", "external"] = "external"


class CallGraph:
    """Function-level execution graph."""

    def __init__(self):
        self.nodes: dict[str, FunctionNode] = {}
        self.edges: list[CallEdge] = []
        self.nx_graph = nx.DiGraph()

    def add_node(self, node: FunctionNode):
        self.nodes[node.id] = node
        self.nx_graph.add_node(node.id, **node.__dict__)

    def add_edge(self, edge: CallEdge):
        self.edges.append(edge)
        self.nx_graph.add_edge(edge.caller_id, edge.callee_id, type=edge.call_type)

    def compute_metrics(self) -> dict[str, dict]:
        """Compute structural metrics for all function nodes."""
        # DFS depth (execution chain length)
        # Using longest simple path is expensive, so we just use recursive eccentricity or simple out-chain length for DAG parts
        # Fan-in and fan-out are simply in-degree and out-degree.
        
        metrics = {}
        # Find recursive components
        try:
            cycles = list(nx.simple_cycles(self.nx_graph))
            recursive_nodes = {n for cycle in cycles for n in cycle}
        except nx.NetworkXNoCycle:
            recursive_nodes = set()

        for node_id in self.nodes:
            in_deg = self.nx_graph.in_degree(node_id)
            out_deg = self.nx_graph.out_degree(node_id)
            
            # DFS depth calculation (max path length from this node to any leaf, ignoring cycles)
            # For a quick heuristic, we use single_source_shortest_path_length and take the max
            paths = nx.single_source_shortest_path_length(self.nx_graph, node_id)
            depth = max(paths.values()) if paths else 0

            metrics[node_id] = {
                "fan_in": in_deg,
                "fan_out": out_deg,
                "call_depth": depth,
                "recursive": node_id in recursive_nodes
            }
        return metrics


def build_call_graph(project: ProjectIR) -> CallGraph:
    """Build a global function-level call graph across the project."""
    cg = CallGraph()

    # Pass 1: Register all available functions/methods across the project
    # Mapping to help resolve imports and calls
    global_funcs: dict[str, str] = {}  # base_name -> node_id
    
    for file_ir in project.files:
        for func in file_ir.functions:
            node_id = f"{file_ir.file_path}::{func.name}"
            cg.add_node(FunctionNode(node_id, file_ir.file_path, func.name, is_async=func.is_async))
            global_funcs[func.name] = node_id
            
        for cls in file_ir.classes:
            for method in cls.methods:
                node_id = f"{file_ir.file_path}::{cls.name}::{method.name}"
                cg.add_node(FunctionNode(node_id, file_ir.file_path, method.name, class_name=cls.name, is_async=method.is_async))
                # Methods can be resolved via Class.method or self.method
                global_funcs[f"{cls.name}.{method.name}"] = node_id
                global_funcs[f"self.{method.name}"] = node_id

    # Pass 2: Map calls to edges
    for file_ir in project.files:
        # Build local resolution map (imports + locals)
        local_scope = {}
        for func in file_ir.functions:
            local_scope[func.name] = f"{file_ir.file_path}::{func.name}"
        for cls in file_ir.classes:
            for method in cls.methods:
                local_scope[f"{cls.name}.{method.name}"] = f"{file_ir.file_path}::{cls.name}::{method.name}"
                local_scope[f"self.{method.name}"] = f"{file_ir.file_path}::{cls.name}::{method.name}"
                
        # Resolve imports (best effort heuristics)
        for imp in file_ir.imports:
            # If we imported specific names, map them to the module's paths
            # (Note: robust resolution requires full path matching, here we assume global uniqueness or simple names)
            for name in imp.names:
                if name in global_funcs:
                    local_scope[name] = global_funcs[name]
            
            # If module is imported entire, map module.func -> known funcs
            mod_last = imp.module.split(".")[-1]
            for g_name, g_id in global_funcs.items():
                if g_name.startswith(f"{mod_last}."):
                    local_scope[g_name] = g_id

        # Attach edges
        def _attach_edges(caller_id: str, calls: list[str]):
            for call_tok in calls:
                callee_id = local_scope.get(call_tok) or global_funcs.get(call_tok)
                if callee_id:
                    # Determine type
                    if "::" in callee_id and "::" in caller_id and callee_id.split("::")[0] == caller_id.split("::")[0]:
                        ctype = "method" if "self." in call_tok or "::" in call_tok else "local"
                    else:
                        ctype = "imported"
                    cg.add_edge(CallEdge(caller_id, callee_id, ctype))
                else:
                    # External system call or unresolved
                    cg.add_edge(CallEdge(caller_id, call_tok, "external"))

        # Functions
        for func in file_ir.functions:
            caller_id = f"{file_ir.file_path}::{func.name}"
            _attach_edges(caller_id, func.calls)
            
        # Methods
        for cls in file_ir.classes:
            for method in cls.methods:
                caller_id = f"{file_ir.file_path}::{cls.name}::{method.name}"
                _attach_edges(caller_id, method.calls)

    logger.info("Call Graph built: %d nodes, %d edges", len(cg.nodes), len(cg.edges))
    return cg
