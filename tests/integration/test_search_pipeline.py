"""Integration tests for the full search pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from kb_tools.config import Config
from kb_tools.search.engine import SearchEngine


def _make_test_kb(tmp_path: Path) -> Config:
    """Create a minimal test knowledge base."""
    chunks_dir = tmp_path / "data" / "kb-index" / "chunks" / "scripture"
    chunks_dir.mkdir(parents=True)
    chunk = {
        "chunk_id": "scripture/genesis/ch001",
        "doc_id": "scripture/genesis",
        "source_path": "kbmd/scripture/genesis.md",
        "category": "scripture",
        "text": "In the beginning God created heaven and earth.",
        "section_label": "Chapter 1",
        "token_count": 10,
    }
    (chunks_dir / "genesis.jsonl").write_text(json.dumps(chunk) + "\n")
    return Config(project_root=tmp_path)


def test_unified_search_keyword_fallback(tmp_path):
    """SearchEngine falls back to keyword when vector index missing."""
    config = _make_test_kb(tmp_path)
    engine = SearchEngine(config)
    results = engine.search("God created", top_k=5)
    assert len(results) >= 1
    text = results[0].get("text", results[0].get("text_preview", ""))
    assert "God" in text


def test_search_with_context(tmp_path):
    """search_with_context returns formatted context string."""
    config = _make_test_kb(tmp_path)
    engine = SearchEngine(config)
    context = engine.search_with_context("God", top_k=5)
    assert isinstance(context, str)
    assert "Source:" in context or "No relevant" in context
