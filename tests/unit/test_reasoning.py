"""Unit tests for reasoning engine."""

from __future__ import annotations

from kb_tools.reasoning.citations import (
    Citation,
    extract_citations,
    format_citations,
)


def test_extract_ccc_citations():
    """Extract CCC paragraph citations."""
    text = "The Church teaches (CCC §2348) that peace is essential."
    citations = extract_citations(text)
    assert len(citations) == 1
    assert citations[0].reference == "CCC §2348"
    assert "Catechism" in citations[0].document


def test_extract_canon_citations():
    """Extract canon law citations."""
    text = "According to Can. 1234, this is the rule."
    citations = extract_citations(text)
    assert len(citations) == 1
    assert citations[0].reference == "Can. 1234"


def test_extract_scripture_citations():
    """Extract scripture references."""
    text = "As John 3:16 says, God so loved the world."
    citations = extract_citations(text)
    assert len(citations) >= 1
    assert any("John" in c.document for c in citations)


def test_format_citations_deduplicates():
    """format_citations deduplicates identical citations."""
    citations = [
        Citation(document="CCC", reference="CCC §100"),
        Citation(document="CCC", reference="CCC §100"),
        Citation(document="CCC", reference="CCC §200"),
    ]
    result = format_citations(citations)
    assert result.count("CCC §100") == 1
    assert "CCC §200" in result


def test_format_citations_empty():
    """format_citations handles empty list."""
    assert format_citations([]) == "No specific citations found."
