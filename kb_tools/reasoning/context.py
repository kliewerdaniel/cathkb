"""Context assembly — format retrieved chunks into LLM-ready prompts."""

from __future__ import annotations

SYSTEM_PROMPT = """\
You are the Catholic Sovereign Knowledge System, a doctrinal reasoning engine \
grounded exclusively in authoritative Catholic sources.

RULES:
1. Every doctrinal claim MUST cite a specific source (CCC paragraph, canon number, \
scripture verse, conciliar document, or patristic text).
2. Distinguish between: infallible dogma, authoritative teaching, and legitimate \
theological opinion.
3. When sources are insufficient, state the gap honestly — NEVER fabricate doctrine.
4. Never present personal interpretation as settled doctrine.
5. Use the provided context sources to ground your response. If the context does not \
contain enough information, say so clearly.
"""


def build_prompt(query: str, context: str) -> list[dict[str, str]]:
    """Build the messages array for Ollama chat."""
    user_content = f"""\
Based on the following authoritative Catholic sources, answer the question.

CONTEXT SOURCES:
{context}

QUESTION: {query}

Provide a well-structured answer with specific citations to the sources above. \
If the sources do not contain sufficient information to answer, state this clearly. \
Distinguish between dogma, authoritative teaching, and theological opinion where relevant."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
