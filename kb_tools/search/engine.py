"""Unified search engine with fallback chain: vector → keyword → empty."""

from __future__ import annotations

from typing import Any

from kb_tools.config import Config
from kb_tools.search.keyword import KeywordSearch
from kb_tools.search.vector import VectorSearch


class SearchEngine:
    """Unified search with automatic fallback."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._vector = VectorSearch(self.config)
        self._keyword = KeywordSearch(self.config)

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search with fallback: vector → keyword."""
        try:
            results = self._vector.search(query, top_k=top_k)
            if results:
                return results
        except (FileNotFoundError, Exception):
            pass
        return self._keyword.search(query, top_k=top_k)

    def search_with_context(
        self, query: str, top_k: int = 5, max_tokens: int = 3000
    ) -> str:
        """Search and format results as context for LLM."""
        results = self.search(query, top_k=top_k)
        if not results:
            return "No relevant sources found in the knowledge base."

        context_parts: list[str] = []
        total_tokens = 0
        for r in results:
            text = r.get("text", r.get("text_preview", ""))
            token_count = r.get("token_count", len(text.split()))
            if total_tokens + token_count > max_tokens:
                break
            source = r.get("source_path", r.get("doc_id", "unknown"))
            section = r.get("section_label", "")
            header = f"[Source: {source}"
            if section:
                header += f" — {section}"
            header += "]"
            context_parts.append(f"{header}\n\n{text}\n")
            total_tokens += token_count

        return "\n---\n\n".join(context_parts)
