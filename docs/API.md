# API Reference — doc

## `cleaner.py`
**Role**: generic

### `clean_python_cache(`root_dir: str`)` → `None`
> Supprime tous les dossiers __pycache__ et fichiers .pyc dans le projet.
**Calls**: `os.walk, print, os.path.join, shutil.rmtree, dirnames.remove, f.endswith, os.path.join, os.remove`

---

## `pycacheCleaner.py`
**Role**: generic

### `clean_python_cache(`root_dir: str`)` → `None`
> Supprime tous les dossiers __pycache__ et fichiers .pyc dans le projet.
**Calls**: `os.walk, print, os.path.join, shutil.rmtree, dirnames.remove, f.endswith, os.path.join, os.remove`

---

## `src/cli.py`
**Role**: generic

### `main(`path`, `provider`, `model`, `output`, `api_key`, `base_url`, `concurrency`, `verbose`, `live`, `dry_run`)`
> CodeDocAI — Generate documentation from source code using AI.
**Calls**: `click.command, click.option, click.option, click.option, click.option, click.option, click.option, click.option, click.option, click.option`

---

## `src/config.py`
**Role**: config

### Class `LLMProvider`
> Supported LLM providers.

### Class `OllamaConfig`
> Settings for local Ollama instance.

### Class `OpenAIConfig`
> Settings for OpenAI-compatible API.

### Class `AppConfig`
> Top-level application configuration.

---

## `src/generator/api_gen.py`
**Role**: controller

### `generate_api_doc(`project: ProjectIR`, `call_graph: CallGraph`)` → `str`
> Generate a full API reference from IR signatures.
**Calls**: `sorted, '\n'.join, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append`

### `_render_function(`func`, `indent: str`)` → `str`
**Calls**: `', '.join, parts.append, '\n'.join, parts.append, parts.append, ', '.join`

---

## `src/generator/architecture_gen.py`
**Role**: generic

### `generate_architecture_doc(`project: ProjectIR`, `graph: nx.DiGraph`, `file_summaries: dict[str, str]`, `entry_points: list[EntryPoint]`)` → `str`
> Generate ARCHITECTURE.md with dependency diagrams and project topology.
**Calls**: `sorted, '\n'.join, generate_dependency_diagram, file_summaries.get, _role_icon, lines.append, lines.extend, lines.append, len`

### `_role_icon(`role: str`)` → `str`
**Calls**: `icons.get`

---

## `src/generator/mermaid_gen.py`
**Role**: generic

### `generate_dependency_diagram(`graph: nx.DiGraph`)` → `str`
> Render a Mermaid flowchart from the dependency graph.
**Calls**: `lines.append, '\n'.join, node.replace('/', '_').replace, lines.append, u.replace('/', '_').replace, v.replace('/', '_').replace, lines.append, node.replace, u.replace, v.replace`

---

## `src/generator/readme_gen.py`
**Role**: generic

### `generate_readme(`project: ProjectIR`)` → `str`
> Generate a pure USER-CENTRIC README.md.
**Calls**: `'\n'.join`

---

## `src/generator/utils.py`
**Role**: utility

### `sanitize_summary(`text: str`)` → `str`
> Clean LLM output from markdown blocks and preambles.
**Calls**: `re.sub, re.sub, re.sub, text.strip`

---

## `src/graph/builder.py`
**Role**: generic

### `build_dependency_graph(`project: ProjectIR`)` → `nx.DiGraph`
> Create a directed graph where edges represent import relationships.

Nodes are file paths (relative).  An edge A → B means "A imports B".
**Calls**: `nx.DiGraph, _build_file_lookup, graph.add_node, _resolve_import, graph.add_edge, logger.debug, logger.debug, imp.module.startswith`

### `_build_file_lookup(`project: ProjectIR`)` → `dict[str, str]`
> Map possible module names to their file paths.
**Calls**: `PurePosixPath, str(path.with_suffix('')).replace, str, path.with_suffix`

### `_resolve_import(`module: str`, `source_file: str`, `lookup: dict[str, str]`)` → `str | None`
> Try to resolve an import string to a known project file.
**Calls**: `lookup.items, key.endswith`

---

## `src/graph/call_graph.py`
**Role**: generic

### `build_call_graph(`project: ProjectIR`)` → `CallGraph`
> Build a global call graph across all project modules.
**Calls**: `CallGraph, cg.nx_graph.add_node, FunctionNode, cg.nx_graph.add_node, FunctionNode, potential_id.endswith, cg.nx_graph.add_edge, cg.edges.append, cg.edges.append, cg.nx_graph.add_edge`

### Class `FunctionNode`

### Class `CallEdge`

### Class `CallGraph`
> Project-wide call graph.

#### `__init__()`
**Calls**: `nx.DiGraph`

#### `compute_metrics()` → `dict`
**Calls**: `nx.betweenness_centrality, len, self.nx_graph.in_degree, self.nx_graph.out_degree, betweenness.get`

---

## `src/graph/cycles.py`
**Role**: repository

### `detect_cycles(`graph: nx.DiGraph`, `call_graph: CallGraph`)` → `CycleReport`
> Detect circular dependencies using NetworkX.
**Calls**: `list, CycleReport, nx.simple_cycles, SingleCycle, CycleReport, len`

### Class `SingleCycle`

### Class `CycleReport`

---

## `src/graph/exporters.py`
**Role**: generic

### `export_call_graph_json(`call_graph: CallGraph`, `output_dir: Path`)` → `None`
> Export the call graph as a D3-compatible JSON structure.
**Calls**: `(output_dir / 'call_graph.json').write_text, json.dumps`

### `export_ir_csv(`project: ProjectIR`, `output_dir: Path`)` → `None`
> Export flattened IR metrics for easy CSV analysis.
**Calls**: `open, csv.writer, writer.writerow, writer.writerow, len, len, len`

---

## `src/graph/metrics.py`
**Role**: generic

### `compute_metrics(`graph: nx.DiGraph`, `call_graph: CallGraph`, `project: ProjectIR`)` → `list[NodeMetrics]`
> Compute V2 Criticality by blending structural file deps with functional execution bounds.
**Calls**: `sorted, graph.in_degree, graph.out_degree, metrics.append, NodeMetrics`

### `topological_order(`graph: nx.DiGraph`)` → `list[str]`
**Calls**: `list, nx.topological_sort, sorted, list`

### Class `NodeMetrics`

---

## `src/llm/base_provider.py`
**Role**: generic

### Class `BaseLLMProvider`
> All LLM providers (local and external) implement this contract.

#### `summarize(`prompt: str`)` → `str`
> Send a prompt and return the LLM's text response.

#### `is_available()` → `bool`
> Check whether the provider is reachable.

---

## `src/llm/docstring_builder.py`
**Role**: generic

### `build_docstring_prompt(`func: FunctionIR`, `source_code: str`, `role: ModuleRole`)` → `str`
> Construct a prompt for generating a Python/JS/Rust docstring.

---

## `src/llm/fallback.py`
**Role**: generic

### `generate_fallback_summary(`file_ir: FileIR`)` → `str`
> Produce a template-based summary from IR when LLM fails.
**Calls**: `len, len, ' '.join, ', '.join, parts.append, ', '.join, parts.append, ', '.join, parts.append, parts.append`

### `generate_fallback_project_summary(`file_summaries: dict[str, str]`)` → `str`
> Produce a template-based project summary when LLM fails.
**Calls**: `len`

---

## `src/llm/ollama_provider.py`
**Role**: generic

### Class `OllamaProvider`
> Local LLM via Ollama HTTP API.

#### `__init__(`config: OllamaConfig`)` → `None`
**Calls**: `httpx.Client`

#### `summarize(`prompt: str`)` → `str`
**Calls**: `range, logger.error, self._client.post, resp.raise_for_status, resp.json().get, logger.error, logger.warning, time.sleep, logger.warning, time.sleep`

#### `is_available()` → `bool`
> Check if Ollama is running AND the configured model is present.
**Calls**: `self._client.get, resp.json().get, any, logger.info, resp.json, m.get('name', '').startswith, m.get`

---

## `src/llm/openai_provider.py`
**Role**: generic

### Class `OpenAIProvider`
> External LLM via OpenAI-compatible chat completions API.

#### `__init__(`config: OpenAIConfig`)` → `None`
**Calls**: `httpx.Client`

#### `summarize(`prompt: str`)` → `str`
**Calls**: `range, logger.error, self._client.post, resp.raise_for_status, resp.json, logger.warning, time.sleep`

#### `is_available()` → `bool`
**Calls**: `self._client.get`

---

## `src/llm/prompt_builder.py`
**Role**: generic

### `build_file_summary_prompt(`file_ir: FileIR`, `source_code: str`, `whitelist: set[str]`, `incoming_calls: list[str]`, `imported_by: list[str]`, `imports_from: list[str]`)` → `str`
> Build a rich grounded prompt for high-fidelity summary.
**Calls**: `lines.extend, '\n'.join, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append`

### `build_batch_summary_prompt(`batch_data: list[tuple[FileIR, set[str]]]`)` → `str`
> Analyze multiple utility files and return a JSON mapping [path -> summary].
**Calls**: `files_info.append, len, json.dumps, list`

### `build_project_summary_prompt(`project: ProjectIR`, `file_summaries: dict[str, str]`, `entry_points: list[EntryPoint]`, `metrics: list[NodeMetrics]`)` → `str`
> Build a high-level architectural overview prompt.
**Calls**: `lines.append, lines.extend, '\n'.join, lines.append, sorted, lines.append, len, file_summaries.get`

---

## `src/mutator/source_writer.py`
**Role**: generic

### `inject_docstring(`file_path: Path`, `function_name: str`, `docstring: str`)` → `bool`
> Inject a docstring into a Python function (stub for now).
**Calls**: `logger.info`

---

## `src/orchestrator.py`
**Role**: generic

### `run_pipeline(`config: AppConfig`)` → `None`
> Execute the full documentation generation pipeline.
**Calls**: `time.time, config.project_path.resolve, output_dir.mkdir, console.print, load_ir, time.time, list, time.time, ProjectIR, time.time`

### `_get_provider(`config: AppConfig`)`
**Calls**: `OpenAIProvider, OllamaProvider`

---

## `src/parser/base_parser.py`
**Role**: generic

### `get_parser(`language: str`)` → `AbstractParser`
> Factory: return the right parser for a language string.
**Calls**: `_registry.get, PythonParser, JSParser, JSParser, RustParser, ValueError`

### Class `AbstractParser`

#### `parse(`path: Path`, `relative_path: str`)` → `FileIR`
> Parse a source file and return its IR.

---

## `src/parser/js_parser.py`
**Role**: generic

### Class `JSParser`
> Lightweight JS/TS parser using regex patterns.

#### `parse(`file_path: Path`, `relative_path: str`)` → `FileIR`
**Calls**: `file_path.read_text, FileIR, self._extract_imports, self._extract_functions, self._extract_classes`

#### `_extract_imports(`source: str`)` → `list[ImportIR]`
**Calls**: `_IMPORT_RE.finditer, m.group, imports.append, m.group, m.group, m.group, m.group, n.strip, names.insert, ImportIR`

#### `_extract_functions(`source: str`)` → `list[FunctionIR]`
**Calls**: `_FUNCTION_RE.finditer, _ARROW_RE.finditer, funcs.append, funcs.append, self._match_to_func, self._match_to_func`

#### `_extract_classes(`source: str`)` → `list[ClassIR]`
**Calls**: `_CLASS_RE.finditer, m.group, m.group, classes.append, ClassIR, source[:m.start()].count, m.start`

#### `_match_to_func(`m: re.Match`)` → `FunctionIR`
**Calls**: `FunctionIR, m.group, ParameterIR, raw_params.split, p.strip, m.group, bool, p.split(':')[0].strip, m.group, (m.groupdict().get('ret') or '').strip`

---

## `src/parser/python_parser.py`
**Role**: generic

### Class `PythonParser`
> Extracts IR from Python source files using the stdlib `ast` module.

#### `parse(`file_path: Path`, `relative_path: str`)` → `FileIR`
**Calls**: `file_path.read_text, FileIR, ast.parse, logger.warning, FileIR, ast.get_docstring, self._extract_imports, self._extract_functions, self._extract_classes, str`

#### `_extract_imports(`tree: ast.Module`)` → `list[ImportIR]`
**Calls**: `ast.walk, isinstance, isinstance, imports.append, imports.append, ImportIR, ImportIR`

#### `_extract_functions(`tree: ast.Module`)` → `list[FunctionIR]`
> Extract top-level functions (not methods inside classes).
**Calls**: `self._build_function_ir, ast.iter_child_nodes, isinstance`

#### `_extract_classes(`tree: ast.Module`)` → `list[ClassIR]`
**Calls**: `ast.iter_child_nodes, isinstance, classes.append, self._build_function_ir, ClassIR, isinstance, ast.get_docstring, self._unparse_node, self._unparse_node`

#### `_build_function_ir(`node: ast.FunctionDef | ast.AsyncFunctionDef`)` → `FunctionIR`
**Calls**: `self._extract_params, self._extract_calls, FunctionIR, self._unparse_node, ast.get_docstring, isinstance, self._unparse_node`

#### `_extract_params(`args: ast.arguments`)` → `list[ParameterIR]`
**Calls**: `params.append, ParameterIR, self._unparse_node`

#### `_extract_calls(`node: ast.AST`)` → `list[str]`
> Collect names of all function/method calls inside a node.
**Calls**: `ast.walk, isinstance, calls.append, self._unparse_node`

#### `_unparse_node(`node: ast.AST | None`)` → `str`
> Safely convert an AST node back to its source string.
**Calls**: `ast.unparse`

---

## `src/parser/rust_parser.py`
**Role**: generic

### Class `RustParser`

#### `parse(`path: Path`, `relative_path: str`)` → `FileIR`
**Calls**: `path.read_text, FileIR, re.finditer, re.finditer, re.finditer, re.finditer, re.finditer, file_ir.imports.append, file_ir.imports.append, match.group`

#### `_parse_func_match(`match: re.Match`)` → `FunctionIR`
**Calls**: `match.group, match.group, params_raw.split, FunctionIR, match.group, match.group(5).strip, match.group, p.split, params.append, match.group`

---

## `src/scanner/file_discovery.py`
**Role**: generic

### `_load_gitignore(`project_root: Path`)` → `pathspec.PathSpec | None`
> Load .gitignore patterns from the project root.
**Calls**: `gitignore.exists, open, pathspec.PathSpec.from_lines`

### `discover_files(`project_root: Path`, `supported_extensions: list[str]`, `exclude_dirs: list[str]`)` → `Iterator[DiscoveredFile]`
> Walk the project tree and yield source files, respecting .gitignore.
**Calls**: `project_root.resolve, _load_gitignore, project_root.rglob, d.lower, any, file_path.relative_to(project_root).as_posix, detect_language, logger.debug, file_path.is_file, file_path.suffix.lower`

### Class `DiscoveredFile`
> A source file discovered during scanning.

---

## `src/scanner/language_detect.py`
**Role**: generic

### `detect_language(`file_path: Path`)` → `Language`
> Return the language for a given file path based on its extension.
**Calls**: `_EXT_MAP.get, file_path.suffix.lower`

### Class `Language`
> Supported programming languages.

---

## `src/semantic/enricher.py`
**Role**: generic

### `enrich_file_ir(`file_ir: FileIR`)` → `FileIR`
**Calls**: `_detect_role, _enrich_function, _enrich_function`

### `_enrich_function(`func: FunctionIR`)`
**Calls**: `_enrich_data_flow, _assign_criticality`

### `_detect_role(`file_ir: FileIR`)` → `ModuleRole`
**Calls**: `file_ir.file_path.lower, _ROLE_PATTERNS.items, pattern.search, cls.name.lower`

### `_detect_side_effects(`func: FunctionIR`)` → `list[SideEffect]`
**Calls**: `' '.join(func.calls).lower, _SIDE_EFFECT_PATTERNS.items, any, ' '.join, effects.append, kw.lower`

### `_enrich_data_flow(`func: FunctionIR`)`
> Identify data flow properties like reads, writes, and purity.
**Calls**: `_detect_side_effects, any, call.lower, any, any, func.io_operations.append, func.reads.append, func.writes.append, call.split, call.split`

### `_assign_criticality(`func: FunctionIR`)`
**Calls**: `len`

---

## `src/semantic/entry_points.py`
**Role**: generic

### `detect_entry_points(`project: ProjectIR`, `call_graph: CallGraph`)` → `list[EntryPoint]`
> Scan the project for executable roots and trace their execution trees.
**Calls**: `nx.descendants, list, EntryPoint, entry_points.append, nx.single_source_shortest_path_length, max, paths.values`

### Class `EntryPoint`
> An execution root node inside the application.

---

## `src/semantic/hallucination_check.py`
**Role**: repository

### `build_symbol_whitelist(`file_ir: FileIR`)` → `set[str]`
**Calls**: `terms.add, terms.update, terms.add, terms.update, terms.add, terms.add, terms.add, terms.update, terms.add, len`

### `check_summary(`file_ir: FileIR`, `summary: str`)` → `HallucinationReport`
**Calls**: `HallucinationReport, build_symbol_whitelist, re.findall, len, _check_missing_critical_components, any, len, max, t.lower, report.flagged_terms.append`

### `_check_missing_critical_components(`file_ir`, `summary`, `report`, `config`)`
**Calls**: `summary.lower, report.missing_critical.append, f.name.lower`

### Class `HallucinationSeverity`

### Class `HallucinationReport`

---

## `src/semantic/ir_export.py`
**Role**: generic

### `export_ir(`project: ProjectIR`, `output_dir: Path`)` → `None`
> Save the project IR to a JSON file for caching and analysis.
**Calls**: `project.model_dump, dump_path.write_text, logger.info, json.dumps`

### `load_ir(`output_dir: Path`)` → `ProjectIR | None`
> Load a previously exported IR from the documentation folder.
**Calls**: `dump_path.exists, json.loads, ProjectIR.model_validate, dump_path.read_text, logger.warning`

### `file_hash(`path: Path`)` → `str`
> Compute a SHA256 hash of a file's content for change detection.
**Calls**: `hashlib.sha256, hasher.hexdigest, open, f.read, hasher.update`

---

## `src/semantic/ir_schema.py`
**Role**: model

### Class `Language`

### Class `SideEffect`

### Class `ModuleRole`

### Class `ParameterIR`

### Class `FunctionIR`

### Class `ClassIR`

### Class `ImportIR`

### Class `FileIR`

### Class `ProjectIR`

---

## `src/semantic/validator.py`
**Role**: generic

### `validate_project_ir(`project: ProjectIR`)` → `ValidationResult`
> Validate the entire project IR for completeness and consistency.
**Calls**: `ValidationResult, symbol_counts.items, _validate_file, _count_symbol, _count_symbol, result.ambiguous_symbols.append, result.warnings.append, logger.warning`

### `_validate_file(`file_ir: FileIR`, `result: ValidationResult`)` → `None`
> Check a single file IR for issues.
**Calls**: `result.warnings.append, result.warnings.append`

### `_count_symbol(`counts: dict[str, int]`, `name: str`)` → `None`
**Calls**: `counts.get`

### Class `ValidationResult`
> Outcome of validating a ProjectIR.

---

## `tests/test_call_graph.py`
**Role**: test

### `test_call_graph_resolution()`
**Calls**: `ProjectIR, FileIR, FileIR, build_call_graph, cg.compute_metrics, len, len, FunctionIR, FunctionIR`

---

## `tests/test_data_flow.py`
**Role**: test

### `test_data_flow_enrichment()`
**Calls**: `FunctionIR, _enrich_data_flow, FunctionIR, _enrich_data_flow`

---

## `tests/test_entry_points.py`
**Role**: test

### `test_detect_entry_points()`
**Calls**: `ProjectIR, FileIR, build_call_graph, detect_entry_points, len, FunctionIR, FunctionIR`

---

## `tests/test_graph.py`
**Role**: test

### `test_graph_builder_and_metrics()`
**Calls**: `ProjectIR, build_dependency_graph, graph.has_edge, graph.has_edge, graph.has_edge, CallGraph, compute_metrics, next, detect_cycles, graph.number_of_nodes`

### `test_cycle_detection()`
**Calls**: `ProjectIR, build_dependency_graph, CallGraph, detect_cycles, len, FileIR, FileIR, ImportIR, ImportIR`

---

## `tests/test_hallucination.py`
**Role**: test

### `test_hallucination_check_clean()`
**Calls**: `FileIR, check_summary, len, ImportIR, FunctionIR, ClassIR, ParameterIR, FunctionIR`

### `test_hallucination_check_flagged()`
**Calls**: `FileIR, check_summary, FunctionIR`

---

## `tests/test_ir_schema.py`
**Role**: model

### `test_role_detection()`
**Calls**: `FileIR, enrich_file_ir, FileIR, enrich_file_ir, FileIR, enrich_file_ir, FileIR, enrich_file_ir`

### `test_side_effect_detection()`
**Calls**: `FileIR, enrich_file_ir, FunctionIR, FunctionIR, FunctionIR, FunctionIR`

---

## `tests/test_parser.py`
**Role**: test

### `test_python_parser(`tmp_path: Path`)`
**Calls**: `file_path.write_text, get_parser, parser.parse, len, len, len, len`

### `test_javascript_parser(`tmp_path: Path`)`
**Calls**: `file_path.write_text, get_parser, parser.parse, len, len, len`

### `test_rust_parser(`tmp_path: Path`)`
**Calls**: `file_path.write_text, get_parser, parser.parse, len, len, len, len`

---

## `tests/test_scanner.py`
**Role**: test

### `test_detect_language()`
**Calls**: `detect_language, detect_language, detect_language, detect_language, detect_language, detect_language, Path, Path, Path, Path`

---
