"""AST-driven text mutator for safely injecting docstrings into source files."""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from codedocai.semantic.ir_schema import FunctionIR, Language

logger = logging.getLogger(__name__)


def inject_docstring(file_path: Path, func: FunctionIR, new_docstring: str, language: Language) -> bool:
    """Inject or replace a docstring into the source file text safely.
    
    Returns True if the file was modified, False otherwise.
    """
    if language != Language.PYTHON:
        logger.warning(f"Live docstring injection not yet supported for {language.value}")
        return False

    try:
        source = file_path.read_text(encoding="utf-8")
        updated_source = _inject_python_docstring(source, func, new_docstring)
        
        if source != updated_source:
            file_path.write_text(updated_source, encoding="utf-8")
            return True
            
    except Exception as e:
        logger.error(f"Failed to mutate {file_path}: {e}")
        
    return False


def _inject_python_docstring(source: str, func: FunctionIR, new_docstring: str) -> str:
    """Uses Python's AST to find exact line bounds for injection."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

    lines = source.splitlines()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
            
        # Match the exact function by name and start line
        if node.name == func.name and node.lineno == func.line_start:
            if not node.body:
                continue

            first_stmt = node.body[0]
            is_docstring = (
                isinstance(first_stmt, ast.Expr) and 
                isinstance(first_stmt.value, ast.Constant) and 
                isinstance(first_stmt.value.value, str)
            )

            # Determine correct indentation
            # Extract indentation from the 'def' line
            def_line = lines[node.lineno - 1]
            base_indent = def_line[:len(def_line) - len(def_line.lstrip())]
            indent = base_indent + "    "
            
            # Format docstring properly (handle multi-line gracefully if needed, though prompts aim for 1-3 lines)
            clean_doc = new_docstring.strip().replace('"""', "'''") # Prevent quote clashes
            
            # If docstring is multiline, indent subsequent lines
            doc_lines = clean_doc.split("\n")
            if len(doc_lines) > 1:
                joined_doc = f"\n{indent}".join(doc_lines)
                formatted_doc = f'{indent}"""\n{indent}{joined_doc}\n{indent}"""'
            else:
                formatted_doc = f'{indent}"""{clean_doc}"""'

            if is_docstring:
                # Replace existing docstring precise bounds
                start_idx = first_stmt.lineno - 1
                end_idx = first_stmt.end_lineno
                
                new_lines = lines[:start_idx] + [formatted_doc] + lines[end_idx:]
                return "\n".join(new_lines) + "\n"
            else:
                # Insert before the first physical statement of the function
                insert_idx = first_stmt.lineno - 1
                
                # If there's an empty line right before the first statement, we maintain it
                new_lines = lines[:insert_idx] + [formatted_doc] + lines[insert_idx:]
                return "\n".join(new_lines) + "\n"

    return source
