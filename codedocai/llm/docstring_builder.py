"""Prompts for generating in-code docstrings via LLM."""

from __future__ import annotations

from codedocai.semantic.ir_schema import FunctionIR, ModuleRole


def build_docstring_prompt(func: FunctionIR, source_code: str, role: ModuleRole) -> str:
    """Construct a strict prompt instructing the LLM to generate a raw docstring."""
    
    # Determine length constraint
    if role in (ModuleRole.CONFIG, ModuleRole.MODEL) or func.criticality == "LOW":
        length_constraint = "Write exactly 1 concise sentence explaining what this function does."
    else:
        length_constraint = "Write 2 to 3 concise sentences explaining what this function does and its primary side-effects."

    # Identify known side effects to force inclusion in the reasoning
    effects = []
    if func.mutates_state:
        effects.append("It mutates state.")
    if func.network_access:
        effects.append("It makes network calls.")
    if func.db_access:
        effects.append("It accesses a database.")
    
    effect_str = " ".join(effects)
    if effect_str:
        effect_str = f"Ensure the docstring subtly mentions: {effect_str}"

    prompt = (
        f"You are a professional code documenter. Write a docstring for the function `{func.name}`.\n\n"
        "RULES:\n"
        "1. Output ONLY the raw text of the docstring.\n"
        "2. DO NOT include the `\"\"\"` or `/**` quote markers.\n"
        "3. DO NOT include the function signature or any code.\n"
        "4. DO NOT use markdown formatting (` ``` `).\n"
        f"5. {length_constraint}\n"
        f"{effect_str}\n\n"
        "SOURCE CODE:\n"
        "```\n"
        f"{source_code}\n"
        "```\n\n"
        "RAW DOCSTRING TEXT:"
    )
    
    return prompt
