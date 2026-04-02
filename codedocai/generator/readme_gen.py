from codedocai.semantic.ir_schema import ProjectIR
from codedocai.generator.utils import sanitize_summary

def generate_readme(project: ProjectIR) -> str:
    """Generate a pure user-centric README.md (Tutorial/Overview)."""
    lines = [f"# {project.project_name} — Documentation Engine", ""]

    # High-level summary
    if project.summary:
        lines.append("## Overview")
        lines.append(sanitize_summary(project.summary))
        lines.append("")

    lines.append("## 🚀 Key Features")
    lines.append("- **Precise Code Intelligence**: Uses deterministic AST parsing to map your codebase with zero hallucinations.")
    lines.append("- **Execution-Aware**: Understands real behavior by tracing entry points and call graphs.")
    lines.append("- **Strict Grounding**: Documentation is derived exclusively from real code symbols (IR).")
    lines.append("- **Automated Refinement**: Self-checks summaries to eliminate inaccuracies.")
    lines.append("")

    lines.append("## 🛠️ Getting Started (Tutorial)")
    lines.append("Follow these steps to generate high-precision documentation for your project.")
    lines.append("")
    lines.append("### 1. Installation")
    lines.append("Ensure you have Python 3.10+ and the required dependencies installed:")
    lines.append("```bash")
    lines.append("pip install -r requirements.txt")
    lines.append("```")
    lines.append("")
    lines.append("### 2. Prepare your LLM")
    lines.append("By default, CodeDocAI uses **Ollama** for local inference. Ensure it is running:")
    lines.append("```bash")
    lines.append("ollama run gemma3:1b")
    lines.append("```")
    lines.append("")
    lines.append("### 3. Generate Documentation")
    lines.append("Run the CLI tool against your source code directory. The output will be saved to a `docs/` folder by default.")
    lines.append("```bash")
    lines.append("python -m codedocai.cli --path ./your-project --model gemma3:1b")
    lines.append("```")
    lines.append("")
    lines.append("### 4. Continuous Integration")
    lines.append("You can integrate CodeDocAI into your CI/CD pipeline to keep your documentation in sync with your code.")
    lines.append("")

    lines.append("## 📖 Full Documentation")
    lines.append("For a deeper look into the system, refer to the following documents:")
    lines.append("")
    lines.append("- [**API Reference**](API.md) — Detailed function/class signatures and call chains.")
    lines.append("- [**Architecture Overview**](ARCHITECTURE.md) — Dependency graphs, execution flow, and project structure.")
    lines.append("")

    return "\n".join(lines)
