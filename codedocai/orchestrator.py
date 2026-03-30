"""Orchestrator — main pipeline runner tying all layers together."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from codedocai.config import AppConfig, LLMProvider
from codedocai.generator.api_gen import generate_api_doc
from codedocai.generator.architecture_gen import generate_architecture_doc
from codedocai.generator.readme_gen import generate_readme
from codedocai.graph.builder import build_dependency_graph
from codedocai.graph.cycles import detect_cycles
from codedocai.graph.metrics import compute_metrics, topological_order
from codedocai.llm.base_provider import BaseLLMProvider
from codedocai.llm.fallback import generate_fallback_project_summary, generate_fallback_summary
from codedocai.llm.ollama_provider import OllamaProvider
from codedocai.llm.openai_provider import OpenAIProvider
from codedocai.llm.prompt_builder import build_file_summary_prompt, build_project_summary_prompt
from codedocai.parser.base_parser import get_parser
from codedocai.scanner.file_discovery import discover_files
from codedocai.semantic.enricher import enrich_file_ir
from codedocai.semantic.ir_schema import ProjectIR
from codedocai.semantic.validator import validate_project_ir

logger = logging.getLogger(__name__)
console = Console()


def run_pipeline(config: AppConfig) -> None:
    """Execute the full documentation generation pipeline."""
    start = time.time()
    project_root = config.project_path.resolve()
    project_name = project_root.name

    console.print(f"\n[bold cyan]CodeDocAI[/] — Generating docs for [bold]{project_name}[/]\n")

    # ── Step 1: Scan ────────────────────────────────────────────────
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Scanning files...", total=None)
        files = list(discover_files(project_root, config.supported_extensions, config.exclude_dirs))
        progress.update(task, description=f"Found {len(files)} source files")

    if not files:
        console.print("[yellow]No source files found. Check your path and extensions.[/]")
        return

    # ── Step 2: Parse ───────────────────────────────────────────────
    project = ProjectIR(project_name=project_name, root_path=str(project_root))

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Parsing...", total=len(files))
        for discovered in files:
            try:
                parser = get_parser(discovered.language.value)
                file_ir = parser.parse(discovered.path, discovered.relative_path)
                file_ir = enrich_file_ir(file_ir)
                project.files.append(file_ir)
            except ValueError:
                logger.debug("No parser for %s, skipping", discovered.relative_path)
            progress.advance(task)

    # ── Step 3: Validate ────────────────────────────────────────────
    validation = validate_project_ir(project)
    if validation.warnings:
        console.print(f"[yellow]Validation warnings: {len(validation.warnings)}[/]")
        for w in validation.warnings[:5]:
            console.print(f"  ⚠ {w}")

    # ── Step 4: Graph ───────────────────────────────────────────────
    graph = build_dependency_graph(project)
    cycle_report = detect_cycles(graph)
    metrics = compute_metrics(graph)
    topo_order = topological_order(graph)

    console.print(f"[green]Graph built:[/] {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    if cycle_report.has_cycles:
        console.print(f"[yellow]⚠ {len(cycle_report.cycles)} cycle(s) detected[/]")

    # ── Step 5: LLM Summaries ───────────────────────────────────────
    provider = _get_provider(config)
    use_llm = provider is not None and provider.is_available()

    if use_llm:
        console.print(f"[green]LLM provider:[/] {config.provider.value}")
    else:
        console.print("[yellow]LLM unavailable — using fallback templates[/]")

    file_summaries: dict[str, str] = {}

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Summarizing...", total=len(project.files))
        for file_ir in project.files:
            if use_llm:
                prompt = build_file_summary_prompt(file_ir)
                summary = provider.summarize(prompt)
                if not summary.strip():
                    summary = generate_fallback_summary(file_ir)
            else:
                summary = generate_fallback_summary(file_ir)

            file_ir.summary = summary
            file_summaries[file_ir.file_path] = summary
            progress.advance(task)

    # Project-level summary
    if use_llm:
        prompt = build_project_summary_prompt(project, file_summaries)
        project.summary = provider.summarize(prompt)
        if not project.summary.strip():
            project.summary = generate_fallback_project_summary(file_summaries)
    else:
        project.summary = generate_fallback_project_summary(file_summaries)

    # ── Step 6: Generate Docs ───────────────────────────────────────
    output_dir = project_root / config.output_dir
    output_dir.mkdir(exist_ok=True)

    readme = generate_readme(project, file_summaries)
    api_doc = generate_api_doc(project)
    arch_doc = generate_architecture_doc(project, graph, metrics, cycle_report)

    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    (output_dir / "API.md").write_text(api_doc, encoding="utf-8")
    (output_dir / "ARCHITECTURE.md").write_text(arch_doc, encoding="utf-8")

    elapsed = time.time() - start
    console.print(f"\n[bold green]✓ Done![/] Generated docs in [bold]{output_dir}[/] ({elapsed:.1f}s)")


def _get_provider(config: AppConfig) -> BaseLLMProvider | None:
    """Instantiate the configured LLM provider."""
    if config.provider == LLMProvider.OLLAMA:
        return OllamaProvider(config.ollama)
    elif config.provider == LLMProvider.OPENAI:
        return OpenAIProvider(config.openai)
    return None
