"""Test for Data Flow tracking (Reads, Writes, Purity)."""

from src.semantic.ir_schema import FunctionIR
from src.semantic.enricher import _enrich_data_flow

def test_data_flow_enrichment():
    # 1. Dirty function
    dirty_func = FunctionIR(name="save_user", calls=["open", "db.insert", "print", "requests.get"])
    _enrich_data_flow(dirty_func)
    
    assert "open" in dirty_func.reads
    assert "open" in dirty_func.writes
    assert "insert" in dirty_func.writes
    assert "requests." in dirty_func.io_operations
    assert dirty_func.mutates_state is True
    assert dirty_func.has_io is True
    assert dirty_func.network_access is True
    assert dirty_func.db_access is False
    assert dirty_func.criticality in ["HIGH", "MEDIUM", "LOW"]

    # 2. Pure function
    pure_func = FunctionIR(name="add", calls=["print", "math.sqrt"])
    _enrich_data_flow(pure_func)
    
    assert pure_func.reads == []
    assert pure_func.writes == []
    assert pure_func.io_operations == []
    assert pure_func.mutates_state is False
    assert pure_func.has_io is False
    assert pure_func.network_access is False
    assert pure_func.db_access is False
    assert pure_func.criticality == "LOW"
