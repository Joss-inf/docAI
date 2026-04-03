"""Exporters for graph and IR data."""

import json
import csv
from pathlib import Path
from src.graph.call_graph import CallGraph
from src.semantic.ir_schema import ProjectIR

def export_call_graph_json(call_graph: CallGraph, output_dir: Path) -> None:
    """Export the call graph as a D3-compatible JSON structure."""
    nodes = [{"id": n, "label": call_graph.nodes[n].name if n in call_graph.nodes else n} for n in call_graph.nx_graph.nodes]
    links = [{"source": u, "target": v} for u, v in call_graph.nx_graph.edges]
    
    data = {"nodes": nodes, "links": links}
    (output_dir / "call_graph.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

def export_ir_csv(project: ProjectIR, output_dir: Path) -> None:
    """Export flattened IR metrics for easy CSV analysis."""
    path = output_dir / "metrics_export.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Functions", "Classes", "Imports", "Role", "Summary"])
        for file_ir in project.files:
            writer.writerow([
                file_ir.file_path,
                len(file_ir.functions),
                len(file_ir.classes),
                len(file_ir.imports),
                file_ir.role.value,
                file_ir.summary[:100] if file_ir.summary else ""
            ])
