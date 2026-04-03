"""Orchestrator — main pipeline runner tying all layers together."""

from __future__ import annotations

import json
import logging
import time
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import AppConfig, LLMProvider
from src.generator.api_gen import generate_api_doc
from src.generator.architecture_gen import generate_architecture_doc
from src.generator.readme_gen import generate_readme
from src.graph.builder import build_dependency_graph
from src.graph.call_graph import build_call_graph
from src.graph.cycles import detect_cycles
from src.graph.metrics import compute_metrics, topological_order
from src.semantic.entry_points import detect_entry_points
from src.llm.fallback import generate_fallback_project_summary, generate_fallback_summary
from src.llm.ollama_provider import OllamaProvider
from src.llm.openai_provider import OpenAIProvider
from src.llm.prompt_builder import build_file_summary_prompt, build_project_summary_prompt
from src.llm.docstring_builder import build_docstring_prompt
from src.mutator.source_writer import inject_docstring
from src.parser.base_parser import get_parser
from src.scanner.file_discovery import discover_files
from src.semantic.enricher import enrich_file_ir
from src.semantic.hallucination_check import check_summary
from src.semantic.ir_export import export_ir, file_hash, load_ir
from src.graph.exporters import export_call_graph_json, export_ir_csv
from src.semantic.ir_schema import ProjectIR

logger = logging.getLogger(__name__)
console = Console()


def run_pipeline(config: AppConfig) -> None:
    """Execute the full documentation generation pipeline."""
    metrics_data = {}
    time_total_start = time.time()
    
    project_root = config.project_path.resolve()
    project_name = project_root.name
    output_dir = project_root / config.output_dir
    output_dir.mkdir(exist_ok=True)

    console.print(f"\n[bold cyan]CodeDocAI[/] — Generating docs for [bold]{project_name}[/]\n")

    # Load cache
    cached_project = load_ir(output_dir)
    cached_files = {f.file_path: f for f in cached_project.files} if cached_project else {}
    reused_count = 0

    # ── Step 1: Scan ────────────────────────────────────────────────
    t0 = time.time()
    files = list(discover_files(project_root, config.supported_extensions, config.exclude_dirs))
    metrics_data["time_scan"] = time.time() - t0

    # ── Step 2: Parse ───────────────────────────────────────────────
    t0 = time.time()
    project = ProjectIR(project_name=project_name, root_path=str(project_root))
    
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Parsing...", total=len(files))
        for discovered in files:
            current_hash = file_hash(discovered.path)
            cached_file = cached_files.get(discovered.relative_path)
            
            if cached_file and cached_file.file_hash == current_hash:
                project.files.append(cached_file)
                reused_count += 1
            else:
                parser = get_parser(discovered.language.value)
                if parser:
                    file_ir = parser.parse(discovered.path, discovered.relative_path)
                    file_ir.file_hash = current_hash
                    file_ir = enrich_file_ir(file_ir)
                    project.files.append(file_ir)
            progress.advance(task)
    metrics_data["time_parse"] = time.time() - t0

    # ── Step 3: Graph & Metrics ─────────────────────────────────────
    t0 = time.time()
    graph = build_dependency_graph(project)
    call_graph = build_call_graph(project)
    cycle_report = detect_cycles(graph, call_graph)
    metrics = compute_metrics(graph, call_graph, project)
    entry_points = detect_entry_points(project, call_graph)
    metrics_data["time_graph"] = time.time() - t0

    # ── Step 3.5: LLM Setup ────────────────────────────────────────
    provider = _get_provider(config)
    use_llm = provider and provider.is_available()

    # ── Step 4: LLM Summaries ───────────────────────────────────────
    if use_llm:
        console.print(f"[green]LLM provider:[/] {config.provider.value}")
    
    file_summaries: dict[str, str] = {}
    hallucination_flags = 0
    lock = threading.Lock()

    def _process_single(file_ir):
        nonlocal hallucination_flags
        if file_ir.summary:
            with lock: file_summaries[file_ir.file_path] = file_ir.summary
            return
        if not use_llm:
            with lock: 
                file_ir.summary = generate_fallback_summary(file_ir)
                file_summaries[file_ir.file_path] = file_ir.summary
            return

        imported_by = list(graph.predecessors(file_ir.file_path)) if file_ir.file_path in graph else []
        imports_from = list(graph.successors(file_ir.file_path)) if file_ir.file_path in graph else []
        is_high = any(f.criticality == "HIGH" for f in file_ir.functions) or any(m.methods and any(meth.criticality == "HIGH" for meth in m.methods) for m in file_ir.classes)
        is_ep = any(ep.file_path == file_ir.file_path for ep in entry_points)
        source_code = (config.project_path / file_ir.file_path).read_text(encoding="utf-8", errors="replace") if (is_high or is_ep) else ""
        
        from src.semantic.hallucination_check import build_symbol_whitelist, check_summary
        whitelist = build_symbol_whitelist(file_ir)
        incoming_calls = [e.caller_id.split("::")[-1] for e in call_graph.edges if e.callee_id.startswith(file_ir.file_path)]
        
        prompt = build_file_summary_prompt(file_ir, source_code, whitelist=whitelist, incoming_calls=incoming_calls, imported_by=imported_by, imports_from=imports_from)
        summary = provider.summarize(prompt)
        
        if not summary.strip(): summary = generate_fallback_summary(file_ir)
        else:
            h_report = check_summary(file_ir, summary)
            if h_report.flagged_terms:
                refine_prompt = f"{prompt}\n\nRe-write strictly following IR. Failed terms: {', '.join(h_report.flagged_terms)}"
                summary = provider.summarize(refine_prompt)
                h_report = check_summary(file_ir, summary)
                with lock: hallucination_flags += len(h_report.flagged_terms)

        with lock:
            file_ir.summary = summary
            file_summaries[file_ir.file_path] = summary

    def _process_batch(batch_files):
        nonlocal hallucination_flags
        from src.semantic.hallucination_check import build_symbol_whitelist
        batch_data = [(f, build_symbol_whitelist(f)) for f in batch_files if not f.summary]
        if not batch_data: return
        
        from src.llm.prompt_builder import build_batch_summary_prompt
        prompt = build_batch_summary_prompt(batch_data)
        raw_response = provider.summarize(prompt)
        
        try:
            clean_json = re.sub(r"```json\s*", "", raw_response, flags=re.IGNORECASE)
            clean_json = re.sub(r"```\s*", "", clean_json).strip()
            summaries_dict = json.loads(clean_json)
            for f, _ in batch_data:
                summary = summaries_dict.get(f.file_path, "").strip()
                if not summary: _process_single(f)
                else:
                    with lock:
                        f.summary = summary
                        file_summaries[f.file_path] = summary
        except Exception:
            for f, _ in batch_data: _process_single(f)

    critical = []
    utility = []
    for f in project.files:
        if f.summary: 
            file_summaries[f.file_path] = f.summary
            continue
        is_high = any(func.criticality == "HIGH" for func in f.functions) or any(m.methods and any(meth.criticality == "HIGH" for meth in m.methods) for m in f.classes)
        is_ep = any(ep.file_path == f.file_path for ep in entry_points)
        if is_high or is_ep: critical.append(f)
        else: utility.append(f)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Summarizing...", total=len(project.files))
        progress.advance(task, reused_count)
        
        with ThreadPoolExecutor(max_workers=config.concurrency) as executor:
            futures = [executor.submit(_process_single, f) for f in critical]
            for i in range(0, len(utility), 5):
                futures.append(executor.submit(_process_batch, utility[i:i+5]))
            for future in as_completed(futures):
                progress.advance(task)

    # Project-level summary
    if use_llm and (not cached_project or not cached_project.summary or reused_count < len(project.files)):
        prompt = build_project_summary_prompt(project, file_summaries, entry_points, metrics)
        project.summary = provider.summarize(prompt)
    elif cached_project:
        project.summary = cached_project.summary
    
    metrics_data["time_llm"] = time.time() - t0

    # ── Step 5: Export ─────────────────────────────────────────────
    t0 = time.time()
    export_ir(project, output_dir)
    export_call_graph_json(call_graph, output_dir)
    export_ir_csv(project, output_dir)
    metrics_data["time_export"] = time.time() - t0

    # ── Step 6: Docs ───────────────────────────────────────────────
    t0 = time.time()
    (output_dir / "README.md").write_text(generate_readme(project), encoding="utf-8")
    (output_dir / "API.md").write_text(generate_api_doc(project, call_graph), encoding="utf-8")
    (output_dir / "ARCHITECTURE.md").write_text(generate_architecture_doc(project, graph, file_summaries, entry_points), encoding="utf-8")
    metrics_data["time_total"] = time.time() - time_total_start
    (output_dir / "metrics.json").write_text(json.dumps(metrics_data, indent=2), encoding="utf-8")
    console.print(f"\n[bold green]✓ Done![/] ({metrics_data['time_total']:.1f}s)")


def _get_provider(config: AppConfig):
    if config.provider == LLMProvider.OLLAMA:
        return OllamaProvider(config.ollama)
    return OpenAIProvider(config.openai)
