"""CLI entry point for CodeDocAI."""

from __future__ import annotations

import logging
from pathlib import Path

import click

from codedocai.config import AppConfig, LLMProvider
from codedocai.orchestrator import run_pipeline


@click.command()
@click.option(
    "--path", "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Path to the project folder to document.",
)
@click.option(
    "--provider",
    type=click.Choice(["ollama", "openai"], case_sensitive=False),
    default="ollama",
    help="LLM provider to use (default: ollama).",
)
@click.option(
    "--model", "-m",
    default=None,
    help="Override the LLM model name.",
)
@click.option(
    "--output", "-o",
    default="docs",
    help="Output directory name (default: docs).",
)
@click.option(
    "--api-key",
    default=None,
    help="API key for OpenAI-compatible provider.",
)
@click.option(
    "--base-url",
    default=None,
    help="Override the provider base URL.",
)
@click.option(
    "--concurrency", "-c",
    type=int,
    default=4,
    help="Number of parallel LLM requests (default: 4).",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose logging.",
)
@click.option(
    "--live",
    is_flag=True,
    help="Auto-inject missing docstrings into source files using LLM.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Report missing docstrings without modifying source files.",
)
def main(path, provider, model, output, api_key, base_url, verbose, live, dry_run, concurrency):
    """CodeDocAI — Generate documentation from source code using AI."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s %(name)s: %(message)s")

    config = AppConfig(
        project_path=Path(path),
        output_dir=output,
        provider=LLMProvider(provider),
        live=live,
        dry_run=dry_run,
        concurrency=concurrency,
    )

    if model:
        if config.provider == LLMProvider.OLLAMA:
            config.ollama.model = model
        else:
            config.openai.model = model

    if api_key:
        config.openai.api_key = api_key

    if base_url:
        if config.provider == LLMProvider.OLLAMA:
            config.ollama.base_url = base_url
        else:
            config.openai.base_url = base_url

    run_pipeline(config)


if __name__ == "__main__":
    main()
