"""Gap detection — identify insufficient source coverage."""

from __future__ import annotations

from kb_tools.config import Config
from kb_tools.search.engine import SearchEngine


class GapDetector:
    """Detect when the knowledge base lacks sufficient sources."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._search = SearchEngine(self.config)

    def has_sufficient_sources(
        self,
        query: str,
        min_results: int = 2,
        min_score: float = 0.3,
    ) -> bool:
        """Check if enough relevant sources exist for a query."""
        results = self._search.search(query, top_k=5)
        if len(results) < min_results:
            return False
        relevant = [
            r for r in results if r.get("score", 0) >= min_score
        ]
        return len(relevant) >= min_results

    def gap_message(self, query: str) -> str:
        """Return an honest gap statement when sources are insufficient."""
        results = self._search.search(query, top_k=3)
        if not results:
            return (
                "I do not have sufficient authoritative sources "
                "in the knowledge base to answer this question. "
                "The Catholic Knowledge System operates from "
                "a curated corpus of magisterial documents, "
                "Scripture, canon law, and Church Fathers. "
                "Please try rephrasing your question or consult "
                "the approved source hierarchy."
            )
        categories = set(r.get("category", "unknown") for r in results)
        found = ", ".join(categories)
        return (
            f"I found limited sources on this topic "
            f"(from: {found}), but not enough to provide a "
            "comprehensive doctrinal answer. The sources I "
            "have may not cover this specific question "
            "adequately. For authoritative guidance, please "
            "consult the Catechism of the Catholic Church, "
            "relevant conciliar documents, or a qualified "
            "theologian."
        )
