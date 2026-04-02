# doc — Documentation Engine

## Overview
CodeDocAI utilizes the `codedocai` library, which provides a CLI for generating documentation. The `codedocai` library, and its components, form the core of the project. It leverages OpenAI models for document generation and utilizes a configuration system to manage LLM providers and API keys. The `orchestrator` module manages the document generation workflow, and the `mutator` module inserts docstrings into source code. Finally, the `graph` module defines dependency relationships through a graph data structure.

## 🚀 Key Features
- **Precise Code Intelligence**: Uses deterministic AST parsing to map your codebase with zero hallucinations.
- **Execution-Aware**: Understands real behavior by tracing entry points and call graphs.
- **Strict Grounding**: Documentation is derived exclusively from real code symbols (IR).
- **Automated Refinement**: Self-checks summaries to eliminate inaccuracies.

## 🛠️ Getting Started (Tutorial)
Follow these steps to generate high-precision documentation for your project.

### 1. Installation
Ensure you have Python 3.10+ and the required dependencies installed:
```bash
pip install -r requirements.txt
```

### 2. Prepare your LLM
By default, CodeDocAI uses **Ollama** for local inference. Ensure it is running:
```bash
ollama run gemma3:1b
```

### 3. Generate Documentation
Run the CLI tool against your source code directory. The output will be saved to a `docs/` folder by default.
```bash
python -m codedocai.cli --path ./your-project --model gemma3:1b
```

### 4. Continuous Integration
You can integrate CodeDocAI into your CI/CD pipeline to keep your documentation in sync with your code.

## 📖 Full Documentation
For a deeper look into the system, refer to the following documents:

- [**API Reference**](API.md) — Detailed function/class signatures and call chains.
- [**Architecture Overview**](ARCHITECTURE.md) — Dependency graphs, execution flow, and project structure.
