"""Unit tests for search engine."""

from __future__ import annotations

import json
from pathlib import Path

from kb_tools.config import Config
from kb_tools.search.keyword import KeywordSearch
from kb_tools.search.vector import VectorSearch


def _make_test_kb(tmp_path: Path) -> Config:
    """Create test KB at the path Config expects."""
    chunks_dir = tmp_path / "data" / "kb-index" / "chunks" / "scripture"
    chunks_dir.mkdir(parents=True)
    chunk = {
        "chunk_id": "test/ch001",
        "doc_id": "test",
        "source_path": "kbmd/test.md",
        "category": "scripture",
        "text": "God created heaven and earth.",
        "section_label": "Chapter 1",
        "token_count": 10,
    }
    (chunks_dir / "test.jsonl").write_text(json.dumps(chunk) + "\n")
    return Config(project_root=tmp_path)


def test_keyword_search_loads_chunks(tmp_path):
    """KeywordSearch loads chunks from JSONL files."""
    config = _make_test_kb(tmp_path)
    search = KeywordSearch(config)
    results = search.search("God", top_k=5)
    assert len(results) >= 1
    assert "God" in results[0].get("text", "")


def test_vector_search_raises_without_index(monkeypatch):
    """VectorSearch raises FileNotFoundError when index missing."""
    monkeypatch.setenv("CATHKB_DATA_DIR", "/nonexistent")
    config = Config()
    search = VectorSearch(config)
    try:
        search.search("test")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
