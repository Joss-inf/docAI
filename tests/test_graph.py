"""Tests for graph builder and metrics."""

from src.graph.builder import build_dependency_graph
from src.graph.cycles import detect_cycles
from src.graph.metrics import compute_metrics, topological_order
from src.graph.call_graph import CallGraph
from src.semantic.ir_schema import FileIR, ImportIR, Language, ProjectIR


def test_graph_builder_and_metrics():
    project = ProjectIR(
        project_name="test",
        root_path=".",
        files=[
            FileIR(
                file_path="main.py",
                language=Language.PYTHON,
                imports=[ImportIR(module="utils.maths"), ImportIR(module="logger")],
            ),
            FileIR(
                file_path="utils/maths.py",
                language=Language.PYTHON,
                imports=[ImportIR(module="logger")],
            ),
            FileIR(
                file_path="logger.py",
                language=Language.PYTHON,
                imports=[],
            ),
        ]
    )

    graph = build_dependency_graph(project)
    
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3
    assert graph.has_edge("main.py", "utils/maths.py")
    assert graph.has_edge("main.py", "logger.py")
    assert graph.has_edge("utils/maths.py", "logger.py")

    cg = CallGraph()
    metrics = compute_metrics(graph, cg, project)

    assert len(metrics) == 3
    # logger.py has 2 in-degree, 0 out-degree
    logger_metric = next(m for m in metrics if m.file_path == "logger.py")
    assert logger_metric.in_degree == 2
    assert logger_metric.out_degree == 0

    # Test cycle detection (none here)
    report = detect_cycles(graph, cg)
    assert report.has_cycles is False


def test_cycle_detection():
    project = ProjectIR(
        project_name="test",
        root_path=".",
        files=[
            FileIR(
                file_path="a.py",
                language=Language.PYTHON,
                imports=[ImportIR(module="b")],
            ),
            FileIR(
                file_path="b.py",
                language=Language.PYTHON,
                imports=[ImportIR(module="a")],
            ),
        ]
    )

    graph = build_dependency_graph(project)
    cg = CallGraph()
    report = detect_cycles(graph, cg)
    
    assert report.has_cycles is True
    assert len(report.cycles) == 1
    assert "a.py" in report.cycles[0].cycle_path
    assert "b.py" in report.cycles[0].cycle_path
