"""Tests for the hallucination shield."""

from src.semantic.hallucination_check import check_summary
from src.semantic.ir_schema import (
    ClassIR,
    FileIR,
    FunctionIR,
    ImportIR,
    Language,
    ParameterIR,
)


def test_hallucination_check_clean():
    file_ir = FileIR(
        file_path="service.py",
        language=Language.PYTHON,
        imports=[ImportIR(module="requests")],
        functions=[
            FunctionIR(
                name="fetch_user",
                params=[ParameterIR(name="user_id", type_hint="int")],
                return_type="dict"
            )
        ],
        classes=[
            ClassIR(name="UserService", methods=[FunctionIR(name="activate")])
        ]
    )

    summary = "The UserService uses requests to fetch_user by user_id and activate them."
    report = check_summary(file_ir, summary)

    assert report.score == 0.0
    assert len(report.flagged_terms) == 0


def test_hallucination_check_flagged():
    file_ir = FileIR(
        file_path="service.py",
        language=Language.PYTHON,
        functions=[FunctionIR(name="do_work")]
    )

    # DatabaseConnection and processData are nowhere in the IR
    summary = "Uses a DatabaseConnection to processData and then do_work."
    report = check_summary(file_ir, summary)

    assert report.score > 0.0
    assert "DatabaseConnection" in report.flagged_terms
    assert "processData" in report.flagged_terms
    assert "do_work" not in report.flagged_terms
