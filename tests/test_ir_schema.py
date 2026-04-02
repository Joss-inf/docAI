"""Tests for IR schema and semantic enrichment."""

from codedocai.semantic.enricher import enrich_file_ir
from codedocai.semantic.ir_schema import (
    FileIR,
    FunctionIR,
    Language,
    ModuleRole,
    SideEffect,
)


def test_role_detection():
    # Controller
    ir = FileIR(file_path="api/user_controller.py", language=Language.PYTHON)
    ir = enrich_file_ir(ir)
    assert ir.role == ModuleRole.CONTROLLER

    # Config
    ir = FileIR(file_path="src/settings.js", language=Language.JAVASCRIPT)
    ir = enrich_file_ir(ir)
    assert ir.role == ModuleRole.CONFIG

    # Repository
    ir = FileIR(file_path="db/repo.py", language=Language.PYTHON)
    ir = enrich_file_ir(ir)
    assert ir.role == ModuleRole.REPOSITORY

    # Fallback to GENERIC
    ir = FileIR(file_path="src/main.rs", language=Language.RUST)
    ir = enrich_file_ir(ir)
    assert ir.role == ModuleRole.GENERIC


def test_side_effect_detection():
    ir = FileIR(
        file_path="test.py",
        language=Language.PYTHON,
        functions=[
            FunctionIR(name="read_file", calls=["open", "read"]),
            FunctionIR(name="fetch_data", calls=["requests.get", "json"]),
            FunctionIR(name="save_db", calls=["session.commit"]),
            FunctionIR(name="pure_func", calls=["len", "sorted"]),
        ]
    )
    ir = enrich_file_ir(ir)

    assert SideEffect.IO in ir.functions[0].side_effects
    assert SideEffect.NETWORK in ir.functions[1].side_effects
    assert SideEffect.DATABASE in ir.functions[2].side_effects
    assert SideEffect.NONE in ir.functions[3].side_effects
