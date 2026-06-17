# Bootstrap: Catholic Sovereign Knowledge System

## Agent Contract

When implementing against this system, you must follow these rules:

### 1. Read Specs Before Writing Code
Always start by reading `.sovereignspec/specs/catholic-knowledge-system.sspec`. Understand the purpose, requirements, constraints, acceptance criteria, and test cases. Specs are the source of truth — code is disposable.

### 2. Honor All Spec Constraints
Constraints are non-negotiable:
- All processing must occur locally
- Only approved Catholic sources for doctrine
- Ollama is the sole LLM runtime
- All artifacts are plain markdown
- The system must operate fully offline after setup

### 3. Update Task Status on Completion
After completing a task, update `.sovereignspec/tasks/catholic-knowledge-system-tasks.md`:
- Change `[ ] pending` to `[x] completed`
- Add completion note: `Completed: YYYY-MM-DD — Brief summary`

### 4. Generate Tests for Every Feature
Every implemented feature needs tests that validate the spec's acceptance criteria. Cover edge cases, error conditions, and boundary values.

### 5. Generate Documentation for Every Module
For every module created or modified, document: what it does, its public API, usage examples, and configuration required.

### 6. Update the Knowledge Graph
After implementing, update `.sovereignspec/graph/graph.json`:
- Add a node for each new module or endpoint
- Add `REFERENCES` edges from spec node to new nodes
- Add `GENERATES` edges from spec to documentation files

### 7. Record Architectural Decisions (ADRs)
If implementation reveals a significant architectural decision not covered by existing ADRs:
1. Find the next ADR number in `.sovereignspec/adr/`
2. Create `.sovereignspec/adr/ADR-NNN.md` with: Context, Decision, Rationale, Alternatives Considered, Consequences

### 8. Register Artifacts
After completing all tasks for a spec, register generated files at `.sovereignspec/agents/opencode/artifacts.json`:
```json
{
  "agent": "opencode",
  "artifacts": [
    {
      "id": "uuid-v4",
      "task_id": "task-uuid",
      "artifact_type": "code|test|doc|config|migration",
      "file_path": "src/posts/service.py",
      "validated": false,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### 9. Update Spec Status Through Lifecycle
As work progresses, update the spec's `status` field:
- Start at `draft`
- Move to `validated` after validation passes
- Move to `approved` after review
- Move to `active` when implementation begins
- Move to `implemented` when code is written
- Move to `verified` when all tests pass
- Move to `archived` when stable

## Quick Start

```bash
# 1. Verify Ollama is running
ollama serve

# 2. Pull required models
ollama pull qwen2.5-coder:32b
ollama pull nomic-embed-text

# 3. Harvest sources
./skills/catholic_source_harvest.sh

# 4. Build knowledge base
./skills/build_kbmd_from_sources.sh

# 5. Build indexes
python3 kb-tools/build-indexes.py

# 6. Start web UI
python3 kb-tools/server.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  CLI     │  │  Web UI  │  │  MCP     │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │              │              │                   │
│  ┌────▼──────────────▼──────────────▼─────┐            │
│  │           Search Engine                 │            │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │            │
│  │  │ Vector  │ │Keyword  │ │ Agent   │  │            │
│  │  │ Search  │ │ Search  │ │ Reason  │  │            │
│  │  └────┬────┘ └────┬────┘ └────┬────┘  │            │
│  │       └───────────┼───────────┘        │            │
│  └───────────────────┼────────────────────┘            │
│                      │                                  │
│  ┌───────────────────▼────────────────────┐            │
│  │           Knowledge Base                │            │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │            │
│  │  │ kbmd/   │ │kb-index │ │ sources │  │            │
│  │  │ (docs)  │ │ (index) │ │ (raw)   │  │            │
│  │  └─────────┘ └─────────┘ └─────────┘  │            │
│  └────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Source Harvesting** (`skills/catholic_source_harvest.sh`)
   - Downloads HTML from approved sources
   - Stores in `sources/raw/`

2. **Markdown Normalization** (`skills/build_kbmd_from_sources.sh`)
   - Converts HTML to structured markdown
   - Categorizes into `kbmd/` subdirectories
   - Preserves citations and references

3. **Index Building** (`kb-tools/build-indexes.py`)
   - Creates document catalog
   - Generates searchable chunks
   - Builds vector embeddings
   - Maps topics to documents
   - Extracts cross-references

4. **Query Processing** (`kb-tools/engine.py`)
   - Routes queries to appropriate search strategy
   - Retrieves relevant context
   - Grounds responses in cited sources
