# ADR-001: Local-First Architecture

## Status
Accepted

## Date
2026-06-15

## Context
The Catholic Knowledge System requires a trustworthy, reproducible, and private knowledge base for doctrinal research. Cloud-based solutions introduce privacy concerns, dependency on external services, and potential data leakage. The system must operate in environments without internet access after initial setup.

## Decision
Adopt a local-first architecture using:
- Ollama for LLM inference (qwen2.5-coder:32b)
- nomic-embed-text for vector embeddings
- Local filesystem for all data storage
- Markdown as the universal artifact format

## Rationale
1. **Privacy**: No doctrinal queries or sources leave the machine
2. **Reproducibility**: Same inputs always produce the same outputs
3. **Independence**: No cloud API dependencies after source harvesting
4. **Portability**: Markdown files are human-readable and version-controllable
5. **Sovereignty**: Full control over the knowledge corpus and reasoning engine

## Alternatives Considered
- **Cloud LLM APIs**: Rejected due to privacy concerns and ongoing costs
- **Vector databases (ChromaDB/Qdrant)**: Rejected for simplicity; filesystem-based approach is sufficient
- **PostgreSQL/SQLite**: Rejected for overkill; markdown files serve as the durable store

## Consequences
- Must manage Ollama model updates manually
- Large corpus requires efficient chunking and indexing
- No real-time collaboration (single-user system)
- All computation happens locally (CPU/GPU requirements)
