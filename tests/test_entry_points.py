"""Test Entry Point identification and DFS tree extraction."""

from codedocai.semantic.entry_points import detect_entry_points
from codedocai.graph.call_graph import build_call_graph
from codedocai.semantic.ir_schema import ProjectIR, FileIR, FunctionIR

def test_detect_entry_points():
    project = ProjectIR(project_name="Test", root_path="/test")
    file1 = FileIR(file_path="cli.py", language="python", functions=[
        FunctionIR(name="main_cli", decorators=["@click.command"], calls=["start_server"]),
        FunctionIR(name="start_server", calls=[])
    ])
    project.files = [file1]
    
    cg = build_call_graph(project)
    eps = detect_entry_points(project, cg)
    
    assert len(eps) == 1
    assert eps[0].type == "CLI"
    assert eps[0].function_id == "cli.py::main_cli"
    
    # Needs to match exactly the descendant ID returned
    assert "cli.py::start_server" in eps[0].reachable_functions
    assert eps[0].execution_depth == 1
