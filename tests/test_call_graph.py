"""Test Call Graph execution mapping."""

from codedocai.graph.call_graph import build_call_graph
from codedocai.semantic.ir_schema import ProjectIR, FileIR, FunctionIR

def test_call_graph_resolution():
    project = ProjectIR(project_name="Test", root_path="/test")
    file1 = FileIR(file_path="main.py", language="python", functions=[
        FunctionIR(name="start", calls=["process_data", "db_save"])
    ])
    file2 = FileIR(file_path="utils.py", language="python", functions=[
        FunctionIR(name="process_data", calls=[])
    ])
    project.files = [file1, file2]
    
    cg = build_call_graph(project)
    
    assert len(cg.nodes) == 2
    assert len(cg.edges) == 2
    
    edges = {(e.caller_id, e.callee_id, e.call_type) for e in cg.edges}
    assert ("main.py::start", "utils.py::process_data", "imported") in edges
    assert ("main.py::start", "db_save", "external") in edges

    metrics = cg.compute_metrics()
    assert metrics["main.py::start"]["fan_out"] == 2
    assert metrics["utils.py::process_data"]["fan_in"] == 1
