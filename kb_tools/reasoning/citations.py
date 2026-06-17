"""Citation extraction and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Citation:
    """A structured reference to a source passage."""

    document: str
    reference: str
    excerpt: str = ""


# Patterns for common Catholic citation formats
CCC_PATTERN = re.compile(
    r"CCC\s*§?\s*(\d+(?:\s*[-–]\s*\d+)?)", re.IGNORECASE
)
CANON_PATTERN = re.compile(
    r"Can\.\s*(\d+(?:\s*§\s*\d+)?)", re.IGNORECASE
)
SCRIPTURE_PATTERN = re.compile(
    r"\b(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|"
    r"Joshua|Judges|Ruth|1\s*Samuel|2\s*Samuel|"
    r"1\s*Kings|2\s*Kings|1\s*Chronicles|2\s*Chronicles|"
    r"Ezra|Nehemiah|Tobit|Judith|Esther|Job|Psal?ms?|"
    r"Proverbs|Ecclesiastes|Song\s*of\s*Solomon|Wisdom|"
    r"Sirach|Isaiah|Jeremiah|Lamentations|Baruch|"
    r"Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|"
    r"Micah|Nahum|Habakkuk|Zephaniah|Haggai|"
    r"Zechariah|Malachi|1\s*Maccabees|2\s*Maccabees|"
    r"Matthew|Mark|Luke|John|Acts|Romans|"
    r"1\s*Corinthians|2\s*Corinthians|Galatians|"
    r"Ephesians|Philippians|Colossians|"
    r"1\s*Thessalonians|2\s*Thessalonians|"
    r"1\s*Timothy|2\s*Timothy|Titus|Philemon|"
    r"Hebrews|James|1\s*Peter|2\s*Peter|"
    r"1\s*John|2\s*John|3\s*John|Jude|"
    r"Revelation)\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def extract_citations(text: str) -> list[Citation]:
    """Extract structured citations from text."""
    citations: list[Citation] = []

    for match in CCC_PATTERN.finditer(text):
        ref = f"CCC §{match.group(1)}"
        citations.append(
            Citation(document="Catechism of the Catholic Church", reference=ref)
        )

    for match in CANON_PATTERN.finditer(text):
        ref = f"Can. {match.group(1)}"
        citations.append(
            Citation(document="Code of Canon Law", reference=ref)
        )

    for match in SCRIPTURE_PATTERN.finditer(text):
        doc = match.group(1)
        ref = f"{doc} {match.group(2)}"
        citations.append(Citation(document=doc, reference=ref))

    return citations


def format_citations(citations: list[Citation]) -> str:
    """Format citations as a readable list."""
    if not citations:
        return "No specific citations found."
    lines = []
    seen: set[str] = set()
    for c in citations:
        key = f"{c.document}:{c.reference}"
        if key not in seen:
            seen.add(key)
            lines.append(f"- {c.reference} ({c.document})")
    return "\n".join(lines)
