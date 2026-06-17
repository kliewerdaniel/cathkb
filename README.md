# Catholic Sovereign Knowledge System

Local-first doctrinal reasoning engine grounded exclusively in authoritative Catholic sources.

## What It Does

- **Search** 212 documents (85MB) — Scripture, CCC, canon law, liturgy, Church Fathers, encyclicals, Vatican II
- **Ask questions** and receive cited answers grounded in magisterial teaching
- **Generate artifacts** — study guides, timelines, comparisons, doctrinal briefs
- **Runs entirely offline** after initial setup — no data leaves your machine

## Quick Start

```bash
# Clone and setup
git clone https://github.com/danielkliewer/cathkb.git
cd cathkb
./setup.sh

# Activate venv
source .venv/bin/activate

# Ask a question
cathkb query "What does the CCC say about the Eucharist?"

# Search the knowledge base
cathkb query "Real Presence" --no-context

# Generate a study guide
cathkb build -t "Eucharist" -t study-guide

# Start web UI
cathkb serve
```

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com) with `qwen2.5-coder:32b` and `nomic-embed-text` models

```bash
ollama pull qwen2.5-coder:32b
ollama pull nomic-embed-text
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│               User Interface                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │   CLI   │  │  Web UI │  │   MCP   │         │
│  └────┬────┘  └────┬────┘  └────┬────┘         │
│       └────────────┼────────────┘               │
│            ┌───────▼────────┐                    │
│            │ Search Engine  │                    │
│            │ vector → ripgrep│                   │
│            └───────┬────────┘                    │
│            ┌───────▼────────┐                    │
│            │   Reasoning    │                    │
│            │ Ollama + cites │                    │
│            └───────┬────────┘                    │
│       ┌────────────▼────────────┐               │
│       │      Knowledge Base     │               │
│       │  kbmd/ · kb-index/      │               │
│       │  212 docs · 13K chunks  │               │
│       └─────────────────────────┘               │
└─────────────────────────────────────────────────┘
```

## Commands

| Command | Description |
|---------|-------------|
| `cathkb query "..."` | Ask a doctrinal question |
| `cathkb query "..." --no-context` | Search only (no LLM) |
| `cathkb build -t topic -t type` | Generate an artifact |
| `cathkb serve` | Start web UI on :8080 |
| `cathkb build-index` | Rebuild indexes |

## Artifact Types

- `study-guide` — Comprehensive study guide with sources
- `timeline` — Chronological development timeline
- `comparison` — Comparative analysis
- `doctrinal-brief` — Official teaching brief

## Project Structure

```
cathkb/
├── kb_tools/           # Python package
│   ├── cli/            # Click CLI
│   ├── web/            # FastAPI web server
│   ├── mcp/            # MCP server
│   ├── search/         # Vector + keyword search
│   ├── reasoning/      # Ollama-powered reasoning
│   ├── ingest/         # Source harvesting pipeline
│   └── index/          # Index building
├── data/
│   ├── kbmd/           # 212 normalized documents
│   ├── kb-index/       # Chunks, embeddings, catalog
│   └── outputs/        # Generated artifacts
├── tests/
├── .sovereignspec/     # SDD specs, ADRs, knowledge graph
└── scripts/            # Cross-platform build scripts
```

## Cross-Platform Releases

GitHub Actions builds standalone binaries on every tagged release:

- `cathkb-linux` — Linux x86_64
- `cathkb-macos` — macOS universal
- `cathkb-windows` — Windows x86_64

## Source Hierarchy

All doctrinal content comes from approved sources only:

1. **Vatican.va** — Official Holy See documents
2. **USCCB.org** — United States Conference of Catholic Bishops
3. **EWTN.com** — Eternal Word Television Network
4. **New Advent** — Church Fathers and historical texts

## License

MIT
