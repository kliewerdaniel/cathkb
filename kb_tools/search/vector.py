"""Vector search using pre-built embeddings and Ollama."""

from __future__ import annotations

import json
from typing import Any

import numpy as np

from kb_tools.config import Config


class VectorSearch:
    """Semantic search over the pre-built embedding index."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._embeddings: np.ndarray | None = None
        self._chunks: list[dict[str, Any]] | None = None
        self._chunk_map: dict[str, int] | None = None

    def _load_index(self) -> None:
        if self._embeddings is not None:
            return
        index_path = self.config.embeddings_dir / "index.bin"
        chunks_path = self.config.embeddings_dir / "chunks.json"
        if not index_path.exists() or not chunks_path.exists():
            raise FileNotFoundError(
                f"Embedding index not found at {index_path}. "
                "Run 'cathkb build' to generate indexes."
            )
        with open(chunks_path) as f:
            self._chunks = json.load(f)
        raw = index_path.read_bytes()
        n_chunks = len(self._chunks)
        self._embeddings = np.frombuffer(raw, dtype=np.float32).reshape(n_chunks, -1)
        self._chunk_map = {c["chunk_id"]: i for i, c in enumerate(self._chunks)}

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a query string using Ollama."""
        import httpx

        resp = httpx.post(
            f"{self.config.ollama_base_url}/api/embeddings",
            json={"model": self.config.ollama_embed_model, "prompt": query},
            timeout=30,
        )
        resp.raise_for_status()
        return np.array(resp.json()["embedding"], dtype=np.float32)

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search for relevant chunks using cosine similarity."""
        self._load_index()
        assert self._embeddings is not None and self._chunks is not None

        q_vec = self.embed_query(query)
        norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(q_vec)
        norms = np.where(norms == 0, 1.0, norms)
        similarities = self._embeddings @ q_vec / norms
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            chunk = dict(self._chunks[idx])
            chunk["score"] = float(similarities[idx])
            results.append(chunk)
        return results
