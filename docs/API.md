# API Reference — doc

## `codedocai/cli.py`
**Role**: generic | **Language**: python

### `main(`path`, `provider`, `model`, `output`, `api_key`, `base_url`, `verbose`)`
> CodeDocAI — Generate documentation from source code using AI.

---

## `codedocai/config.py`
**Role**: config | **Language**: python

### Class `LLMProvider` (str, Enum)
> Supported LLM providers.

### Class `OllamaConfig` (BaseModel)
> Settings for local Ollama instance.

### Class `OpenAIConfig` (BaseModel)
> Settings for OpenAI-compatible API.

### Class `AppConfig` (BaseModel)
> Top-level application configuration.

---

## `codedocai/generator/api_gen.py`
**Role**: controller | **Language**: python

### `generate_api_doc(`project: ProjectIR`)` → `str`
> Generate a full API.md from the project IR.

### `_render_file_api(`file_ir: FileIR`)` → `str`
> Render the API section for a single file.

### `_render_function(`func`, `indent: str`)` → `str`
> Render a single function/method as Markdown.

---

## `codedocai/generator/architecture_gen.py`
**Role**: generic | **Language**: python

### `generate_architecture_doc(`project: ProjectIR`, `graph: nx.DiGraph`, `metrics: list[NodeMetrics]`, `cycle_report: CycleReport`)` → `str`
> Generate ARCHITECTURE.md with dependency diagrams and analysis.

---

## `codedocai/generator/mermaid_gen.py`
**Role**: generic | **Language**: python

### `generate_dependency_diagram(`graph: nx.DiGraph`)` → `str`
> Render the project dependency graph as a Mermaid flowchart.

### `generate_module_diagram(`file_ir_list`)` → `str`
> Render a class/function overview diagram for a set of files.

### `_sanitize(`name: str`)` → `str`
> Convert a file path to a valid Mermaid node ID.

---

## `codedocai/generator/readme_gen.py`
**Role**: generic | **Language**: python

### `generate_readme(`project: ProjectIR`, `file_summaries: dict[str, str]`)` → `str`
> Generate a README.md combining project summary and file overviews.

### `_role_icon(`role: str`)` → `str`

---

## `codedocai/graph/builder.py`
**Role**: generic | **Language**: python

### `build_dependency_graph(`project: ProjectIR`)` → `nx.DiGraph`
> Create a directed graph where edges represent import relationships.

Nodes are file paths (relative).  An edge A → B means "A imports B".

### `_build_file_lookup(`project: ProjectIR`)` → `dict[str, str]`
> Map possible module names to their file paths.

### `_resolve_import(`module: str`, `source_file: str`, `lookup: dict[str, str]`)` → `str | None`
> Try to resolve an import string to a known project file.

---

## `codedocai/graph/cycles.py`
**Role**: repository | **Language**: python

### `detect_cycles(`graph: nx.DiGraph`)` → `CycleReport`
> Find all strongly connected components with more than one node (cycles).

### Class `CycleReport`
> Result of cycle detection in the dependency graph.

---

## `codedocai/graph/metrics.py`
**Role**: model | **Language**: python

### `compute_metrics(`graph: nx.DiGraph`)` → `list[NodeMetrics]`
> Compute in-degree, out-degree, and criticality for each node.

### `topological_order(`graph: nx.DiGraph`)` → `list[str]`
> Return a deterministic topological ordering of nodes.

If the graph has cycles, returns best-effort ordering by
removing back-edges.

### Class `NodeMetrics`
> Metrics for a single node in the dependency graph.

---

## `codedocai/llm/base_provider.py`
**Role**: generic | **Language**: python

### Class `BaseLLMProvider` (ABC)
> All LLM providers (local and external) implement this contract.

#### `summarize(`prompt: str`)` → `str`
> Send a prompt and return the LLM's text response.

#### `is_available()` → `bool`
> Check whether the provider is reachable.

---

## `codedocai/llm/fallback.py`
**Role**: generic | **Language**: python

### `generate_fallback_summary(`file_ir: FileIR`)` → `str`
> Produce a template-based summary from IR when LLM fails.

### `generate_fallback_project_summary(`file_summaries: dict[str, str]`)` → `str`
> Produce a template-based project summary when LLM fails.

---

## `codedocai/llm/ollama_provider.py`
**Role**: generic | **Language**: python

### Class `OllamaProvider` (BaseLLMProvider)
> Local LLM via Ollama HTTP API.

#### `__init__(`config: OllamaConfig`)` → `None`
**Side-effects**: network

#### `summarize(`prompt: str`)` → `str`

#### `is_available()` → `bool`
> Check if Ollama is running AND the configured model is present.

---

## `codedocai/llm/openai_provider.py`
**Role**: generic | **Language**: python

### Class `OpenAIProvider` (BaseLLMProvider)
> External LLM via OpenAI-compatible chat completions API.

#### `__init__(`config: OpenAIConfig`)` → `None`
**Side-effects**: network

#### `summarize(`prompt: str`)` → `str`

#### `is_available()` → `bool`

---

## `codedocai/llm/prompt_builder.py`
**Role**: generic | **Language**: python

### `build_file_summary_prompt(`file_ir: FileIR`)` → `str`
> Build a prompt for summarizing a single file from its IR.

### `build_project_summary_prompt(`project: ProjectIR`, `file_summaries: dict[str, str]`)` → `str`
> Build a prompt for the project-level summary using file summaries.

### `_format_function_sig(`func`)` → `str`
> Format a function signature from its IR.

---

## `codedocai/orchestrator.py`
**Role**: generic | **Language**: python

### `run_pipeline(`config: AppConfig`)` → `None`
> Execute the full documentation generation pipeline.
**Side-effects**: io

### `_get_provider(`config: AppConfig`)` → `BaseLLMProvider | None`
> Instantiate the configured LLM provider.
**Side-effects**: io

---

## `codedocai/parser/base_parser.py`
**Role**: generic | **Language**: python

### `get_parser(`language: str`)` → `AbstractParser`
> Factory: return the right parser for a language string.

### Class `AbstractParser` (ABC)
> Base class for language-specific AST parsers.

Every parser reads a source file and returns a standardised FileIR.

#### `parse(`file_path: Path`, `relative_path: str`)` → `FileIR`
> Parse a single source file and return its IR.

---

## `codedocai/parser/js_parser.py`
**Role**: generic | **Language**: python

### Class `JSParser` (AbstractParser)
> Lightweight JS/TS parser using regex patterns.

#### `parse(`file_path: Path`, `relative_path: str`)` → `FileIR`
**Side-effects**: io

#### `_extract_imports(`source: str`)` → `list[ImportIR]`

#### `_extract_functions(`source: str`)` → `list[FunctionIR]`

#### `_extract_classes(`source: str`)` → `list[ClassIR]`

#### `_match_to_func(`m: re.Match`)` → `FunctionIR`

---

## `codedocai/parser/python_parser.py`
**Role**: generic | **Language**: python

### Class `PythonParser` (AbstractParser)
> Extracts IR from Python source files using the stdlib `ast` module.

#### `parse(`file_path: Path`, `relative_path: str`)` → `FileIR`
**Side-effects**: io

#### `_extract_imports(`tree: ast.Module`)` → `list[ImportIR]`

#### `_extract_functions(`tree: ast.Module`)` → `list[FunctionIR]`
> Extract top-level functions (not methods inside classes).

#### `_extract_classes(`tree: ast.Module`)` → `list[ClassIR]`

#### `_build_function_ir(`node: ast.FunctionDef | ast.AsyncFunctionDef`)` → `FunctionIR`

#### `_extract_params(`args: ast.arguments`)` → `list[ParameterIR]`

#### `_extract_calls(`node: ast.AST`)` → `list[str]`
> Collect names of all function/method calls inside a node.

#### `_unparse_node(`node: ast.AST | None`)` → `str`
> Safely convert an AST node back to its source string.

---

## `codedocai/scanner/file_discovery.py`
**Role**: model | **Language**: python

### `_load_gitignore(`project_root: Path`)` → `pathspec.PathSpec | None`
> Load .gitignore patterns from the project root.
**Side-effects**: io

### `discover_files(`project_root: Path`, `supported_extensions: list[str]`, `exclude_dirs: list[str]`)` → `Iterator[DiscoveredFile]`
> Walk the project tree and yield source files, respecting .gitignore.

### Class `DiscoveredFile`
> A source file discovered during scanning.

---

## `codedocai/scanner/language_detect.py`
**Role**: generic | **Language**: python

### `detect_language(`file_path: Path`)` → `Language`
> Return the language for a given file path based on its extension.

### Class `Language` (str, Enum)
> Supported programming languages.

---

## `codedocai/semantic/enricher.py`
**Role**: generic | **Language**: python

### `enrich_file_ir(`file_ir: FileIR`)` → `FileIR`
> Enrich a FileIR with roles, side-effects, and criticality.

### `_detect_role(`file_ir: FileIR`)` → `ModuleRole`
> Determine the module role from file path + class/decorator names.

### `_detect_side_effects(`func: FunctionIR`)` → `list[SideEffect]`
> Scan call targets for known side-effect patterns.

---

## `codedocai/semantic/ir_schema.py`
**Role**: model | **Language**: python

### Class `Language` (str, Enum)

### Class `SideEffect` (str, Enum)
> Known side-effect categories.

### Class `ModuleRole` (str, Enum)
> Heuristic role assigned during semantic enrichment.

### Class `ParameterIR` (BaseModel)
> A single function/method parameter.

### Class `FunctionIR` (BaseModel)
> Intermediate representation of a function or method.

### Class `ClassIR` (BaseModel)
> Intermediate representation of a class.

### Class `ImportIR` (BaseModel)
> A single import statement.

### Class `FileIR` (BaseModel)
> IR for an entire source file.

### Class `ProjectIR` (BaseModel)
> IR for the entire project.

---

## `codedocai/semantic/validator.py`
**Role**: model | **Language**: python

### `validate_project_ir(`project: ProjectIR`)` → `ValidationResult`
> Validate the entire project IR for completeness and consistency.

### `_validate_file(`file_ir: FileIR`, `result: ValidationResult`)` → `None`
> Check a single file IR for issues.

### `_count_symbol(`counts: dict[str, int]`, `name: str`)` → `None`

### Class `ValidationResult`
> Outcome of validating a ProjectIR.

---
