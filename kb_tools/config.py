"""Configuration — Environment and path management."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _project_root() -> Path:
    """Walk up from this file to find pyproject.toml."""
    here = Path(__file__).resolve().parent
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True)
class Config:
    """Immutable configuration loaded from environment / .env."""

    # Ollama
    ollama_base_url: str = field(default_factory=lambda: _env("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: _env("OLLAMA_MODEL", "qwen2.5-coder:32b"))
    ollama_embed_model: str = field(
        default_factory=lambda: _env("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    )

    # Paths (relative to project root)
    project_root: Path = field(default_factory=_project_root)

    @property
    def kb_dir(self) -> Path:
        return self.project_root / _env("KB_DIR", "data").lstrip("./")

    @property
    def kbmd_dir(self) -> Path:
        return self.project_root / _env("KBMD_DIR", "data/kbmd").lstrip("./")

    @property
    def kb_index_dir(self) -> Path:
        return self.project_root / _env("KB_INDEX_DIR", "data/kb-index").lstrip("./")

    @property
    def outputs_dir(self) -> Path:
        return self.project_root / _env("OUTPUTS_DIR", "data/outputs").lstrip("./")

    @property
    def sources_dir(self) -> Path:
        return self.project_root / _env("SOURCES_DIR", "data/sources").lstrip("./")

    @property
    def embeddings_dir(self) -> Path:
        return self.kb_index_dir / "embeddings"

    @property
    def chunks_dir(self) -> Path:
        return self.kb_index_dir / "chunks"

    @property
    def catalog_path(self) -> Path:
        return self.kb_index_dir / "catalog.json"


def load_config() -> Config:
    """Load configuration from environment."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    return Config()
