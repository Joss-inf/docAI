"""README.md generator — pure user-centric tutorial and project presentation."""

from __future__ import annotations
from src.semantic.ir_schema import ProjectIR

def generate_readme(project: ProjectIR) -> str:
    """Generate a pure USER-CENTRIC README.md."""
    lines = [
        f"# {project.project_name}",
        "",
        "## Overview",
        project.summary if project.summary else "A technical project analyzed by CodeDocAI.",
        "",
        "## Key Features",
        "- **Automated Documentation**: Generates API, Architecture, and README files.",
        "- **AI Grounding**: High-fidelity summaries with IR-based hallucination checks.",
        "- **Performance**: Parallelized pipeline with batch summarization.",
        "",
        "## Getting Started",
        "### Installation",
        "```bash",
        "pip install -r requirements.txt",
        "```",
        "",
        "### Usage",
        "Generate documentation for your project:",
        "```bash",
        "python -m src.cli --path . --model gemma3:1b --concurrency 8",
        "```",
        "",
        "## Architecture",
        "For a detailed technical overview, see [ARCHITECTURE.md](./ARCHITECTURE.md).",
        "For API signatures, see [API.md](./API.md).",
        "",
        "---",
        "*Generated with ❤️ by CodeDocAI*",
    ]
    return "\n".join(lines)
