"""Docstring builder — constructs prompts for generating source-level docstrings."""

from src.semantic.ir_schema import FunctionIR, ModuleRole

def build_docstring_prompt(func: FunctionIR, source_code: str, role: ModuleRole) -> str:
    """Construct a prompt for generating a Python/JS/Rust docstring."""
    return f"Generate a technical docstring for function {func.name} in role {role.value}.\nCode:\n{source_code}"
