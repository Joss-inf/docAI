"""Global configuration for CodeDocAI."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"


class OllamaConfig(BaseModel):
    """Settings for local Ollama instance."""
    base_url: str = "http://localhost:11434"
    model: str = "gemma3:1b"
    timeout_seconds: int = 300
    max_retries: int = 3


class OpenAIConfig(BaseModel):
    """Settings for OpenAI-compatible API."""
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    timeout_seconds: int = 60
    max_retries: int = 3


class AppConfig(BaseModel):
    """Top-level application configuration."""
    project_path: Path = Field(default=Path("."))
    output_dir: str = "docs"
    provider: LLMProvider = LLMProvider.OLLAMA
    ollama: OllamaConfig = OllamaConfig()
    openai: OpenAIConfig = OpenAIConfig()
    max_context_tokens: int = 4096
    supported_extensions: list[str] = Field(
        default=[".py", ".js", ".ts", ".jsx", ".tsx", ".rs"]
    )
    exclude_dirs: list[str] = Field(
        default=["node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"]
    )
    cache_enabled: bool = True
    log_level: str = "INFO"
    live: bool = False
    dry_run: bool = False
    concurrency: int = 4  # Number of parallel LLM requests
