# ADR-003: Two-Phase Pipeline Architecture

## Status
Accepted

## Date
2026-06-15

## Context
Building a comprehensive Catholic knowledge base requires both document ingestion (knowledge construction) and intelligent querying (reasoning engine). These have different computational requirements and should be separated.

## Decision
Implement a two-phase pipeline:
1. **Phase 1 - Knowledge Construction**: Shell scripts for source harvesting, HTML parsing, markdown normalization
2. **Phase 2 - Reasoning Engine**: Agent-driven semantic search, query processing, artifact generation

## Rationale
1. **Separation of Concerns**: Ingestion is I/O bound, reasoning is CPU/GPU bound
2. **Reproducibility**: Knowledge construction can be re-run without affecting reasoning
3. **Modularity**: Each phase can be developed and tested independently
4. **Fallback Strategy**: Vector search → ripgrep → agent knowledge

## Alternatives Considered
- **Monolithic pipeline**: Rejected for complexity and debugging difficulty
- **Event-driven architecture**: Rejected for overkill; sequential pipeline is sufficient
- **Real-time ingestion**: Rejected for simplicity; batch processing is preferred

## Consequences
- Must maintain two separate codebases (shell scripts + Python)
- Phase 1 produces durable artifacts (kbmd/)
- Phase 2 consumes Phase 1 outputs
- Pipeline can be paused and resumed
