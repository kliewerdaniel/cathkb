"""Response generation via Ollama."""

from __future__ import annotations

from typing import Any

import httpx

from kb_tools.config import Config
from kb_tools.reasoning.citations import extract_citations, format_citations
from kb_tools.reasoning.context import build_prompt


class Generator:
    """Generate cited responses using Ollama."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()

    def generate(self, query: str, context: str, stream: bool = False) -> str:
        """Generate a response grounded in the provided context."""
        messages = build_prompt(query, context)

        if stream:
            return self._generate_stream(messages)

        resp = httpx.post(
            f"{self.config.ollama_base_url}/api/chat",
            json={
                "model": self.config.ollama_model,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        return str(data["message"]["content"])

    def _generate_stream(self, messages: list[dict[str, str]]) -> str:
        """Generate with streaming, return final accumulated text."""
        collected: list[str] = []
        with httpx.stream(
            "POST",
            f"{self.config.ollama_base_url}/api/chat",
            json={
                "model": self.config.ollama_model,
                "messages": messages,
                "stream": True,
            },
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    import json

                    data = json.loads(line)
                    content = data.get("message", {}).get("content")
                    if content:
                        collected.append(str(content))
        return "".join(collected)

    def generate_with_citations(
        self, query: str, context: str
    ) -> dict[str, Any]:
        """Generate response and extract citations."""
        response = self.generate(query, context)
        citations = extract_citations(response)
        return {
            "response": response,
            "citations": citations,
            "formatted_citations": format_citations(citations),
        }
