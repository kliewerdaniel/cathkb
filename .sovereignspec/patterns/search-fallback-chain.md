# Pattern: Search Fallback Chain

## Description
The system implements a multi-tier search strategy to ensure query results.

## Chain Order

### 1. Vector Search (Semantic)
- Uses nomic-embed-text embeddings
- Best for conceptual queries
- Requires pre-computed index

### 2. Keyword Search (Full-Text)
- Uses ripgrep for fast pattern matching
- Best for exact terms, citations, references
- Always available (no index required)

### 3. Agent Knowledge
- LLM reasoning from context
- Best for synthesis, comparison, analysis
- Fallback when search yields insufficient results

## Implementation
```python
def search(query, mode="auto"):
    if mode == "semantic" or mode == "auto":
        results = vector_search(query)
        if results:
            return results
    
    if mode == "keyword" or mode == "auto":
        results = keyword_search(query)
        if results:
            return results
    
    return agent_reasoning(query)
```

## Query Routing
- Auto mode: Tries all strategies in order
- Semantic mode: Vector search only
- Keyword mode: Full-text search only
- Research mode: Agent reasoning with retrieved context
