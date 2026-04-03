# doc

## Overview
Here’s a 4-5 sentence architectural overview for the README, focusing on data flow:

The project’s data flows primarily from the entry points, which act as initial gateways for various projects. These entry points utilize the `base_parser` to handle diverse languages and subsequently feed data into the core layers. The `call_graph.py` module then builds a complex call graph representing the system’s operations, enabling analysis and performance evaluation.  Finally, the `semantic/ir_schema.py` and `graph/call_graph.py` modules contribute to the data flow by providing schema definitions and graph-based analysis, ensuring data integrity and efficient processing. This structured flow supports robust project automation and discovery.

## Key Features
- **Automated Documentation**: Generates API, Architecture, and README files.
- **AI Grounding**: High-fidelity summaries with IR-based hallucination checks.
- **Performance**: Parallelized pipeline with batch summarization.

## Getting Started
### Installation
```bash
pip install -r requirements.txt
```

### Usage
Generate documentation for your project:
```bash
python -m src.cli --path . --model gemma3:1b --concurrency 8
```

## Architecture
For a detailed technical overview, see [ARCHITECTURE.md](./ARCHITECTURE.md).
For API signatures, see [API.md](./API.md).

---
*Generated with ❤️ by CodeDocAI*