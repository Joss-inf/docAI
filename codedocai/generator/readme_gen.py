"""README.md generator — project-level overview from LLM summaries and IR."""

from __future__ import annotations

from codedocai.semantic.ir_schema import ProjectIR


def generate_readme(project: ProjectIR, file_summaries: dict[str, str]) -> str:
    """Generate a README.md combining project summary and file overviews."""
    lines = [f"# {project.project_name}", ""]

    # Project summary
    if project.summary:
        lines.append(project.summary)
        lines.append("")

    # File structure overview
    lines.append("## Project Structure")
    lines.append("")
    for file_ir in sorted(project.files, key=lambda f: f.file_path):
        summary = file_summaries.get(file_ir.file_path, "")
        icon = _role_icon(file_ir.role.value)
        lines.append(f"- {icon} **`{file_ir.file_path}`** — {summary}")
    lines.append("")

    # Quick stats
    total_funcs = sum(len(f.functions) for f in project.files)
    total_classes = sum(len(f.classes) for f in project.files)
    lines.append("## Stats")
    lines.append(f"- **Files**: {len(project.files)}")
    lines.append(f"- **Functions**: {total_funcs}")
    lines.append(f"- **Classes**: {total_classes}")
    lines.append("")

    return "\n".join(lines)


def _role_icon(role: str) -> str:
    icons = {
        "controller": "🎮",
        "service": "⚙️",
        "repository": "🗄️",
        "model": "📦",
        "utility": "🔧",
        "config": "⚙️",
        "test": "🧪",
        "generic": "📄",
    }
    return icons.get(role, "📄")
