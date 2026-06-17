"""Keyword search using ripgrep fallback."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from kb_tools.config import Config


class KeywordSearch:
    """Full-text search via ripgrep over chunk files."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._chunks_loaded = False
        self._all_chunks: list[dict[str, Any]] = []

    def _load_chunks(self) -> None:
        if self._chunks_loaded:
            return
        chunks_dir = self.config.kb_index_dir / "chunks"
        for jsonl_file in chunks_dir.rglob("*.jsonl"):
            with open(jsonl_file) as f:
                for line in f:
                    if line.strip():
                        self._all_chunks.append(json.loads(line))
        self._chunks_loaded = True

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search chunk text files using ripgrep, fall back to in-memory."""
        chunks_dir = self.config.kb_index_dir / "chunks"
        if not chunks_dir.exists():
            return []

        try:
            result = subprocess.run(
                ["rg", "-i", "-l", "--max-count", "1", query, str(chunks_dir)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            matching_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        except (FileNotFoundError, subprocess.TimeoutExpired):
            matching_files = []

        if matching_files:
            results = []
            for fpath in matching_files[:top_k]:
                path = Path(fpath)
                if not path.exists():
                    continue
                with open(path) as f:
                    for line in f:
                        if line.strip():
                            chunk = json.loads(line)
                            if query.lower() in chunk.get("text", "").lower():
                                chunk["score"] = 0.5
                                results.append(chunk)
                                break
            return results[:top_k]

        self._load_chunks()
        results = []
        query_lower = query.lower()
        for chunk in self._all_chunks:
            text = chunk.get("text", chunk.get("text_preview", "")).lower()
            if query_lower in text:
                chunk["score"] = 0.5
                results.append(dict(chunk))
                if len(results) >= top_k:
                    break
        return results
