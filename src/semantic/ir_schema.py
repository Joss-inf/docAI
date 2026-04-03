"""Unified Intermediate Representation (IR) — Pydantic models."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    UNKNOWN = "unknown"


class SideEffect(str, Enum):
    IO = "io"
    NETWORK = "network"
    DATABASE = "database"
    PROCESS = "process"
    NONE = "none"


class ModuleRole(str, Enum):
    CONTROLLER = "controller"
    SERVICE = "service"
    REPOSITORY = "repository"
    MODEL = "model"
    UTILITY = "utility"
    CONFIG = "config"
    TEST = "test"
    GENERIC = "generic"


class ParameterIR(BaseModel):
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None


class FunctionIR(BaseModel):
    name: str
    params: list[ParameterIR] = Field(default_factory=list)
    return_type: Optional[str] = None
    decorators: list[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    calls: list[str] = Field(default_factory=list)
    side_effects: list[SideEffect] = Field(default_factory=list)
    is_async: bool = False
    
    # Data Flow & Enrichment
    reads: list[str] = Field(default_factory=list)
    writes: list[str] = Field(default_factory=list)
    io_operations: list[str] = Field(default_factory=list)
    mutates_state: bool = False
    has_io: bool = False
    network_access: bool = False
    db_access: bool = False
    criticality: str = "LOW"
    
    line_start: int = 0
    line_end: int = 0


class ClassIR(BaseModel):
    name: str
    bases: list[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    methods: list[FunctionIR] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


class ImportIR(BaseModel):
    module: str
    names: list[str] = Field(default_factory=list)
    alias: Optional[str] = None
    is_relative: bool = False


class FileIR(BaseModel):
    file_path: str
    language: Language
    imports: list[ImportIR] = Field(default_factory=list)
    functions: list[FunctionIR] = Field(default_factory=list)
    classes: list[ClassIR] = Field(default_factory=list)
    module_docstring: Optional[str] = None
    role: ModuleRole = ModuleRole.GENERIC
    criticality: float = 0.0
    summary: Optional[str] = None
    file_hash: str = ""


class ProjectIR(BaseModel):
    project_name: str
    root_path: str
    files: list[FileIR] = Field(default_factory=list)
    summary: Optional[str] = None
