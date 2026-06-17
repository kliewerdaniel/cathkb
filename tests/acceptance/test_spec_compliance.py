"""Acceptance tests — validate spec acceptance criteria."""

from __future__ import annotations

import json
from pathlib import Path

from kb_tools.config import Config
from kb_tools.reasoning.gaps import GapDetector
from kb_tools.search.engine import SearchEngine


def _make_test_kb(tmp_path: Path) -> Config:
    """Create a minimal test knowledge base with CCC-like content."""
    chunks_dir = tmp_path / "data" / "kb-index" / "chunks" / "magisterium"
    chunks_dir.mkdir(parents=True)
    chunk = {
        "chunk_id": "magisterium/ccc/para-100",
        "doc_id": "magisterium/ccc",
        "source_path": "kbmd/magisterium/ccc/part1.md",
        "category": "magisterium",
        "text": (
            "CCC 100: The Eucharist is the source and summit "
            "of the Christian life. The Eucharist is the "
            "real presence of Jesus Christ under the "
            "appearances of bread and wine."
        ),
        "section_label": "Paragraph 100",
        "token_count": 50,
    }
    (chunks_dir / "ccc.jsonl").write_text(json.dumps(chunk) + "\n")
    return Config(project_root=tmp_path)


def test_gap_detector_no_results(tmp_path):
    """GapDetector reports gap when keyword search finds nothing."""
    config = _make_test_kb(tmp_path)
    detector = GapDetector(config)
    has = detector.has_sufficient_sources("quantum physics")
    assert not has


def test_gap_message_no_results(tmp_path):
    """gap_message returns honest statement when no sources found."""
    config = _make_test_kb(tmp_path)
    detector = GapDetector(config)
    msg = detector.gap_message("quantum physics")
    assert "sufficient" in msg.lower() or "sources" in msg.lower()


def test_search_returns_relevant_results(tmp_path):
    """Search returns results matching the query."""
    config = _make_test_kb(tmp_path)
    engine = SearchEngine(config)
    results = engine.search("Eucharist", top_k=5)
    assert len(results) >= 1
    texts = " ".join(
        r.get("text", r.get("text_preview", "")) for r in results
    )
    assert "Eucharist" in texts
