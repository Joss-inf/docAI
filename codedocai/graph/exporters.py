"""Exporters for Call Graph and IR data into CSV/JSON."""

import csv
import json
from pathlib import Path

from codedocai.graph.call_graph import CallGraph
from codedocai.semantic.ir_schema import ProjectIR


def export_call_graph_json(call_graph: CallGraph, output_dir: Path) -> None:
    """Export the Call Graph to a JSON file."""
    data = {
        "nodes": list(call_graph.nodes),
        "edges": [
            {"caller": e.caller_id, "callee": e.callee_id, "type": e.call_type} 
            for e in call_graph.edges
        ]
    }
    out_path = output_dir / "call_graph.json"
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_ir_csv(project: ProjectIR, output_dir: Path) -> None:
    """Export the flattened IR metrics to a CSV file for analytical ingestion."""
    out_path = output_dir / "ir_metrics.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "file_path", "function_name", "role", "is_async", 
            "mutates_state", "has_io", "network_access", "db_access", "criticality"
        ])
        
        for file_ir in project.files:
            for func in file_ir.functions:
                writer.writerow([
                    file_ir.file_path, func.name, file_ir.role.value, func.is_async,
                    func.mutates_state, func.has_io, func.network_access, func.db_access, func.criticality
                ])
            for cls in file_ir.classes:
                for method in cls.methods:
                    method_name = f"{cls.name}.{method.name}"
                    writer.writerow([
                        file_ir.file_path, method_name, file_ir.role.value, method.is_async,
                        method.mutates_state, method.has_io, method.network_access, method.db_access, method.criticality
                    ])
