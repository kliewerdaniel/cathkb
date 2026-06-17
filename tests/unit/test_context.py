"""Unit tests for context builder."""

from __future__ import annotations

from kb_tools.reasoning.context import SYSTEM_PROMPT, build_prompt


def test_build_prompt_contains_query():
    """build_prompt includes the user query."""
    messages = build_prompt("What is the Eucharist?", "context here")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Eucharist" in messages[1]["content"]


def test_build_prompt_contains_context():
    """build_prompt includes the retrieved context."""
    messages = build_prompt("test", "CCC §1234 says something")
    assert "CCC §1234" in messages[1]["content"]


def test_system_prompt_has_rules():
    """System prompt contains doctrinal rules."""
    assert "cite" in SYSTEM_PROMPT.lower()
    assert "fabricate" in SYSTEM_PROMPT.lower()
