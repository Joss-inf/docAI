"""Unified Intermediate Representation (IR) — Pydantic models.

This schema is language-agnostic: Python, JS, TS, and Rust all produce
the same IR structure so downstream layers never care about the source language.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"


class SideEffect(str, Enum):
    """Known side-effect categories."""
    IO = "io"
    NETWORK = "network"
    DATABASE = "database"
    PROCESS = "process"
    NONE = "none"


class ModuleRole(str, Enum):
    """Heuristic role assigned during semantic enrichment."""
    CONTROLLER = "controller"
    SERVICE = "service"
    REPOSITORY = "repository"
    MODEL = "model"
    UTILITY = "utility"
    CONFIG = "config"
    TEST = "test"
    GENERIC = "generic"


class ParameterIR(BaseModel):
    """A single function/method parameter."""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None


class FunctionIR(BaseModel):
    """Intermediate representation of a function or method."""
    name: str
    params: list[ParameterIR] = Field(default_factory=list)
    return_type: Optional[str] = None
    decorators: list[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    calls: list[str] = Field(default_factory=list)
    side_effects: list[SideEffect] = Field(default_factory=list)
    is_async: bool = False
    line_start: int = 0
    line_end: int = 0


class ClassIR(BaseModel):
    """Intermediate representation of a class."""
    name: str
    bases: list[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    methods: list[FunctionIR] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


class ImportIR(BaseModel):
    """A single import statement."""
    module: str
    names: list[str] = Field(default_factory=list)
    alias: Optional[str] = None
    is_relative: bool = False


class FileIR(BaseModel):
    """IR for an entire source file."""
    file_path: str
    language: Language
    imports: list[ImportIR] = Field(default_factory=list)
    functions: list[FunctionIR] = Field(default_factory=list)
    classes: list[ClassIR] = Field(default_factory=list)
    module_docstring: Optional[str] = None
    role: ModuleRole = ModuleRole.GENERIC
    criticality: float = 0.0
    summary: Optional[str] = None  # Filled by LLM later


class ProjectIR(BaseModel):
    """IR for the entire project."""
    project_name: str
    root_path: str
    files: list[FileIR] = Field(default_factory=list)
    summary: Optional[str] = None  # Filled by LLM later
