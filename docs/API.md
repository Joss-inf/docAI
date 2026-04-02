# API Reference — doc

## Table of Contents
- [Config](#config)
  - [codedocai/config.py](#config)
- [Controller](#controller)
  - [codedocai/generator/api_gen.py](#api-gen)
- [Generic](#generic)
  - [codedocai/cli.py](#cli)
  - [codedocai/generator/architecture_gen.py](#architecture-gen)
  - [codedocai/generator/mermaid_gen.py](#mermaid-gen)
  - [codedocai/generator/readme_gen.py](#readme-gen)
  - [codedocai/graph/builder.py](#builder)
  - [codedocai/graph/exporters.py](#exporters)
  - [codedocai/llm/base_provider.py](#base-provider)
  - [codedocai/llm/docstring_builder.py](#docstring-builder)
  - [codedocai/llm/fallback.py](#fallback)
  - [codedocai/llm/ollama_provider.py](#ollama-provider)
  - [codedocai/llm/openai_provider.py](#openai-provider)
  - [codedocai/llm/prompt_builder.py](#prompt-builder)
  - [codedocai/mutator/source_writer.py](#source-writer)
  - [codedocai/orchestrator.py](#orchestrator)
  - [codedocai/parser/base_parser.py](#base-parser)
  - [codedocai/parser/js_parser.py](#js-parser)
  - [codedocai/parser/python_parser.py](#python-parser)
  - [codedocai/parser/rust_parser.py](#rust-parser)
  - [codedocai/scanner/language_detect.py](#language-detect)
  - [codedocai/semantic/enricher.py](#enricher)
  - [codedocai/semantic/ir_export.py](#ir-export)
  - [pycacheCleaner.py](#pycachecleaner)
- [Model](#model)
  - [codedocai/graph/call_graph.py](#call-graph)
  - [codedocai/graph/metrics.py](#metrics)
  - [codedocai/scanner/file_discovery.py](#file-discovery)
  - [codedocai/semantic/entry_points.py](#entry-points)
  - [codedocai/semantic/ir_schema.py](#ir-schema)
  - [codedocai/semantic/validator.py](#validator)
  - [tests/test_ir_schema.py](#test-ir-schema)
- [Repository](#repository)
  - [codedocai/graph/cycles.py](#cycles)
  - [codedocai/semantic/hallucination_check.py](#hallucination-check)
- [Test](#test)
  - [tests/test_call_graph.py](#test-call-graph)
  - [tests/test_data_flow.py](#test-data-flow)
  - [tests/test_entry_points.py](#test-entry-points)
  - [tests/test_graph.py](#test-graph)
  - [tests/test_hallucination.py](#test-hallucination)
  - [tests/test_parser.py](#test-parser)
  - [tests/test_scanner.py](#test-scanner)
- [Utility](#utility)
  - [codedocai/generator/utils.py](#utils)

## Role: Config
> Configuration and settings

### codedocai/config.py
**Language**: python

#### Class LLMProvider (str, Enum)
> Supported LLM providers.

#### Class OllamaConfig (BaseModel)
> Settings for local Ollama instance.

#### Class OpenAIConfig (BaseModel)
> Settings for OpenAI-compatible API.

#### Class AppConfig (BaseModel)
> Top-level application configuration.

---

## Role: Controller
> Main orchestration logic

### codedocai/generator/api_gen.py
**Language**: python

#### generate_api_doc(project: ProjectIR, call_graph: CallGraph, include_private: bool, noise_calls: set[str] | None, max_flow_calls: int) → str
> Generate a full API.md from the project IR,
grouped by module role and enriched with execution insights.

**Calls:**
- `Path`
- `defaultdict`
- `sorted`

---

## Role: Generic
> Utility and helper modules

### codedocai/cli.py
**Language**: python

#### main(path, provider, model, output, api_key, base_url, verbose, live, dry_run, concurrency)
> CodeDocAI — Generate documentation from source code using AI.

**Calls:**
- `AppConfig`
- `LLMProvider`
- `Path`
- `run_pipeline`

---

### codedocai/generator/architecture_gen.py
**Language**: python

#### generate_architecture_doc(project: ProjectIR, graph: nx.DiGraph, file_summaries: dict[str, str], entry_points: list[EntryPoint]) → str
> Generate ARCHITECTURE.md with dependency diagrams, execution flow, and project structure.

**Calls:**
- `generate_dependency_diagram`
- `role_icon`
- `sanitize_summary`
- `sorted`

---

### codedocai/generator/mermaid_gen.py
**Language**: python

#### generate_dependency_diagram(graph: nx.DiGraph) → str
> Render the project dependency graph as a Mermaid flowchart.

**Calls:**
- `sorted`

#### generate_module_diagram(file_ir_list) → str
> Render a class/function overview diagram for a set of files.

#### generate_call_graph_diagram(call_graph) → str
> Render the function call execution graph as a Mermaid flowchart (Max 30 top edges).

**Calls:**
- `sorted`

---

### codedocai/generator/readme_gen.py
**Language**: python

#### generate_readme(project: ProjectIR) → str
> Generate a pure user-centric README.md (Tutorial/Overview).

**Calls:**
- `sanitize_summary`

---

### codedocai/graph/builder.py
**Language**: python

#### build_dependency_graph(project: ProjectIR) → nx.DiGraph
> Create a directed graph where edges represent import relationships.

Nodes are file paths (relative).  An edge A → B means "A imports B".

**Calls:**
- `graph.add_edge`
- `graph.add_node`
- `nx.DiGraph`

---

### codedocai/graph/exporters.py
**Language**: python

#### export_call_graph_json(call_graph: CallGraph, output_dir: Path) → None
> Export the Call Graph to a JSON file.

**Calls:**
- `out_path.write_text`

#### export_ir_csv(project: ProjectIR, output_dir: Path) → None
> Export the flattened IR metrics to a CSV file for analytical ingestion.

**Calls:**
- `csv.writer`
- `writer.writerow`

---

### codedocai/llm/base_provider.py
**Language**: python

#### Class BaseLLMProvider (ABC)
> All LLM providers (local and external) implement this contract.

##### summarize(prompt: str) → str
> Send a prompt and return the LLM's text response.

##### is_available() → bool
> Check whether the provider is reachable.

---

### codedocai/llm/docstring_builder.py
**Language**: python

#### build_docstring_prompt(func: FunctionIR, source_code: str, role: ModuleRole) → str
> Construct a strict prompt instructing the LLM to generate a raw docstring.

---

### codedocai/llm/fallback.py
**Language**: python

#### generate_fallback_summary(file_ir: FileIR) → str
> Produce a template-based summary from IR when LLM fails.

**Calls:**
- `sorted`

#### generate_fallback_project_summary(file_summaries: dict[str, str]) → str
> Produce a template-based project summary when LLM fails.

---

### codedocai/llm/ollama_provider.py
**Language**: python

#### Class OllamaProvider (BaseLLMProvider)
> Local LLM via Ollama HTTP API.

##### __init__(config: OllamaConfig) → None

**Calls:**
- `httpx.Client`

##### summarize(prompt: str) → str

**Calls:**
- `resp.json`
- `resp.raise_for_status`
- `time.sleep`

##### is_available() → bool
> Check if Ollama is running AND the configured model is present.

**Calls:**
- `resp.json`

---

### codedocai/llm/openai_provider.py
**Language**: python

#### Class OpenAIProvider (BaseLLMProvider)
> External LLM via OpenAI-compatible chat completions API.

##### __init__(config: OpenAIConfig) → None

**Calls:**
- `httpx.Client`

##### summarize(prompt: str) → str

**Calls:**
- `resp.json`
- `resp.raise_for_status`
- `time.sleep`

##### is_available() → bool

---

### codedocai/llm/prompt_builder.py
**Language**: python

#### build_file_summary_prompt(file_ir: FileIR, source_code: str, whitelist: set[str], incoming_calls: list[str] | None, imported_by: list[str] | None, imports_from: list[str] | None) → str
> Build a prompt for summarizing a single file from its IR.

Includes cross-file dependency context when available.

**Calls:**
- `sorted`

#### build_project_summary_prompt(project: ProjectIR, file_summaries: dict[str, str], entry_points: list[EntryPoint] | None, metrics: list[NodeMetrics] | None) → str
> Build a prompt for the project-level summary using file summaries.

#### build_batch_summary_prompt(batch: list[tuple[FileIR, set[str]]]) → str
> Build a prompt for summarizing multiple files at once.

**Calls:**
- `sorted`

---

### codedocai/mutator/source_writer.py
**Language**: python

#### inject_docstring(file_path: Path, func: FunctionIR, new_docstring: str, language: Language) → bool
> Inject or replace a docstring into the source file text safely.

Returns True if the file was modified, False otherwise.

**Calls:**
- `file_path.read_text`
- `file_path.write_text`

---

### codedocai/orchestrator.py
**Language**: python

#### run_pipeline(config: AppConfig) → None
> Execute the full documentation generation pipeline.

**Calls:**
- `(config.project_path / file_ir.file_path).read_text`
- `(output_dir / 'API.md').write_text`
- `(output_dir / 'ARCHITECTURE.md').write_text`
- `(output_dir / 'README.md').write_text`
- `(output_dir / 'metrics.json').write_text`
- _Other internal calls hidden_

---

### codedocai/parser/base_parser.py
**Language**: python

#### get_parser(language: str) → AbstractParser
> Factory: return the right parser for a language string.

**Calls:**
- `JSParser`
- `PythonParser`
- `RustParser`

#### Class AbstractParser (ABC)
> Base class for language-specific AST parsers.

Every parser reads a source file and returns a standardised FileIR.

##### parse(file_path: Path, relative_path: str) → FileIR
> Parse a single source file and return its IR.

---

### codedocai/parser/js_parser.py
**Language**: python

#### Class JSParser (AbstractParser)
> Lightweight JS/TS parser using regex patterns.

##### parse(file_path: Path, relative_path: str) → FileIR

**Calls:**
- `FileIR`
- `file_path.read_text`

---

### codedocai/parser/python_parser.py
**Language**: python

#### Class PythonParser (AbstractParser)
> Extracts IR from Python source files using the stdlib `ast` module.

##### parse(file_path: Path, relative_path: str) → FileIR

**Calls:**
- `FileIR`
- `file_path.read_text`

---

### codedocai/parser/rust_parser.py
**Language**: python

#### Class RustParser (AbstractParser)
> Lightweight Rust parser using regex patterns.

##### parse(file_path: Path, relative_path: str) → FileIR

**Calls:**
- `FileIR`
- `file_path.read_text`

---

### codedocai/scanner/language_detect.py
**Language**: python

#### detect_language(file_path: Path) → Language
> Return the language for a given file path based on its extension.

#### Class Language (str, Enum)
> Supported programming languages.

---

### codedocai/semantic/enricher.py
**Language**: python

#### enrich_file_ir(file_ir: FileIR) → FileIR
> Enrich a FileIR with roles, side-effects, criticality, and data flow.

**Calls:**

---

### codedocai/semantic/ir_export.py
**Language**: python

#### export_ir(project: ProjectIR, output_dir: Path) → Path
> Write the full ProjectIR to a JSON file for debugging / RAG use.

**Calls:**
- `output_path.write_text`
- `project.model_dump`

#### load_ir(output_dir: Path) → ProjectIR | None
> Load a previously exported ProjectIR, if available.

**Calls:**
- `ProjectIR.model_validate`
- `ir_path.exists`
- `ir_path.read_text`

#### file_hash(file_path: Path) → str
> Compute a SHA-256 hash for a file's contents.

**Calls:**
- `file_path.read_bytes`
- `hashlib.sha256`
- `hashlib.sha256(content).hexdigest`

---

### pycacheCleaner.py
**Language**: python

#### clean_python_cache(root_dir: str) → None
> Supprime tous les dossiers __pycache__ et fichiers .pyc dans le projet.

**Calls:**
- `os.walk`

---

## Role: Model

### codedocai/graph/call_graph.py
**Language**: python

#### build_call_graph(project: ProjectIR) → CallGraph
> Build a global function-level call graph across the project.

**Calls:**
- `CallEdge`
- `CallGraph`
- `FunctionNode`
- `cg.add_edge`
- `cg.add_node`

#### Class FunctionNode
> A node representing a function or method in the call graph.

#### Class CallEdge
> A directed edge representing a function call.

#### Class CallGraph
> Function-level execution graph.

##### __init__()

**Calls:**
- `nx.DiGraph`

##### add_node(node: FunctionNode)

##### add_edge(edge: CallEdge)

##### compute_metrics() → dict[str, dict]
> Compute structural metrics for all function nodes.

**Calls:**
- `nx.simple_cycles`
- `nx.single_source_shortest_path_length`

---

### codedocai/graph/metrics.py
**Language**: python

#### compute_metrics(graph: nx.DiGraph, call_graph: CallGraph, project: ProjectIR) → list[NodeMetrics]
> Compute V2 Criticality by blending structural file deps with functional execution bounds.

**Calls:**
- `NodeMetrics`
- `call_graph.compute_metrics`
- `graph.in_degree`
- `graph.out_degree`

#### topological_order(graph: nx.DiGraph) → list[str]
> Return a deterministic topological ordering of nodes.

If the graph has cycles, returns best-effort ordering by
removing back-edges.

**Calls:**
- `nx.topological_sort`
- `sorted`

#### Class NodeMetrics
> Metrics for a single file module in the dependency graph.

---

### codedocai/scanner/file_discovery.py
**Language**: python

#### discover_files(project_root: Path, supported_extensions: list[str], exclude_dirs: list[str]) → Iterator[DiscoveredFile]
> Walk the project tree and yield source files, respecting .gitignore.

**Calls:**
- `DiscoveredFile`
- `detect_language`
- `file_path.is_file`
- `file_path.relative_to`
- `file_path.relative_to(project_root).as_posix`
- _Other internal calls hidden_

#### Class DiscoveredFile
> A source file discovered during scanning.

---

### codedocai/semantic/entry_points.py
**Language**: python

#### detect_entry_points(project: ProjectIR, call_graph: CallGraph) → list[EntryPoint]
> Scan the project for executable roots and trace their execution trees.

**Calls:**
- `EntryPoint`
- `nx.descendants`
- `nx.single_source_shortest_path_length`

#### Class EntryPoint
> An execution root node inside the application.

---

### codedocai/semantic/ir_schema.py
**Language**: python

#### Class Language (str, Enum)

#### Class SideEffect (str, Enum)
> Known side-effect categories.

#### Class ModuleRole (str, Enum)
> Heuristic role assigned during semantic enrichment.

#### Class ParameterIR (BaseModel)
> A single function/method parameter.

#### Class FunctionIR (BaseModel)
> Intermediate representation of a function or method.

#### Class ClassIR (BaseModel)
> Intermediate representation of a class.

#### Class ImportIR (BaseModel)
> A single import statement.

#### Class FileIR (BaseModel)
> IR for an entire source file.

#### Class ProjectIR (BaseModel)
> IR for the entire project.

---

### codedocai/semantic/validator.py
**Language**: python

#### validate_project_ir(project: ProjectIR) → ValidationResult
> Validate the entire project IR for completeness and consistency.

**Calls:**
- `ValidationResult`

#### Class ValidationResult
> Outcome of validating a ProjectIR.

---

### tests/test_ir_schema.py
**Language**: python

#### test_role_detection()

**Calls:**
- `FileIR`
- `enrich_file_ir`

#### test_side_effect_detection()

**Calls:**
- `FileIR`
- `FunctionIR`
- `enrich_file_ir`

---

## Role: Repository

### codedocai/graph/cycles.py
**Language**: python

#### detect_cycles(graph: nx.DiGraph, call_graph: CallGraph) → CycleReport
> Find all strongly connected components in imports and calls.

**Calls:**
- `CycleReport`
- `CycleWarning`
- `nx.strongly_connected_components`
- `sorted`

#### Class CycleWarning
> A detected cycle with analysis of its impact and fixes.

#### Class CycleReport
> Result of cycle detection in the dependency graph.

---

### codedocai/semantic/hallucination_check.py
**Language**: python

#### build_symbol_whitelist(file_ir: FileIR) → set[str]
> Collect all valid identifiers from the IR for grounding.

**Calls:**

#### check_summary(file_ir: FileIR, summary: str) → HallucinationReport
> Cross-check an LLM summary against the file's IR.

Extracts technical terms from the summary and verifies each
one exists somewhere in the IR (function names, class names,
import modules, param names,

**Calls:**
- `HallucinationReport`

#### Class HallucinationReport
> Result of cross-checking a summary against its IR.

---

## Role: Test

### tests/test_call_graph.py
**Language**: python

#### test_call_graph_resolution()

**Calls:**
- `FileIR`
- `FunctionIR`
- `ProjectIR`
- `build_call_graph`
- `cg.compute_metrics`

---

### tests/test_data_flow.py
**Language**: python

#### test_data_flow_enrichment()

**Calls:**
- `FunctionIR`

---

### tests/test_entry_points.py
**Language**: python

#### test_detect_entry_points()

**Calls:**
- `FileIR`
- `FunctionIR`
- `ProjectIR`
- `build_call_graph`
- `detect_entry_points`

---

### tests/test_graph.py
**Language**: python

#### test_graph_builder_and_metrics()

**Calls:**
- `CallGraph`
- `FileIR`
- `ImportIR`
- `ProjectIR`
- `build_dependency_graph`
- _Other internal calls hidden_

#### test_cycle_detection()

**Calls:**
- `CallGraph`
- `FileIR`
- `ImportIR`
- `ProjectIR`
- `build_dependency_graph`
- _Other internal calls hidden_

---

### tests/test_hallucination.py
**Language**: python

#### test_hallucination_check_clean()

**Calls:**
- `ClassIR`
- `FileIR`
- `FunctionIR`
- `ImportIR`
- `ParameterIR`
- _Other internal calls hidden_

#### test_hallucination_check_flagged()

**Calls:**
- `FileIR`
- `FunctionIR`
- `check_summary`

---

### tests/test_parser.py
**Language**: python

#### test_python_parser(tmp_path: Path)

**Calls:**
- `file_path.write_text`
- `get_parser`
- `parser.parse`

#### test_javascript_parser(tmp_path: Path)

**Calls:**
- `file_path.write_text`
- `get_parser`
- `parser.parse`

#### test_rust_parser(tmp_path: Path)

**Calls:**
- `file_path.write_text`
- `get_parser`
- `parser.parse`

---

### tests/test_scanner.py
**Language**: python

#### test_detect_language()

**Calls:**
- `Path`
- `detect_language`

---

## Role: Utility

### codedocai/generator/utils.py
**Language**: python

#### role_icon(role: str) → str
> Return a simple text marker for a module role.

#### sanitize_summary(text: str) → str
> Strip LLM preambles, internal tokens, and code blocks.

---
