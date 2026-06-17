"""Configuration — Environment and path management."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _user_data_dir() -> Path:
    """Return platform-appropriate user data directory."""
    system = sys.platform
    if system == "darwin":
        return Path.home() / "Library" / "Application Support" / "cathkb"
    elif system == "win32":
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(appdata) / "cathkb"
    else:
        return Path.home() / ".local" / "share" / "cathkb"


def _bundled_data_dir() -> Path | None:
    """If running as PyInstaller bundle, return data dir next to binary."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "data"
    return None


def _project_root() -> Path:
    """Walk up from this file to find pyproject.toml."""
    here = Path(__file__).resolve().parent
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent


def _resolve_data_root() -> Path:
    """Find the data directory: env override > bundled > project root."""
    env_override = _env("CATHKB_DATA_DIR")
    if env_override:
        return Path(env_override)

    bundled = _bundled_data_dir()
    if bundled and bundled.exists():
        return bundled

    user_data = _user_data_dir()
    if user_data.exists():
        return user_data

    return _project_root() / "data"


@dataclass(frozen=True)
class Config:
    """Immutable configuration loaded from environment / .env."""

    # Ollama
    ollama_base_url: str = field(
        default_factory=lambda: _env("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    ollama_model: str = field(default_factory=lambda: _env("OLLAMA_MODEL", "qwen2.5-coder:32b"))
    ollama_embed_model: str = field(
        default_factory=lambda: _env("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    )

    # Paths (relative to data root)
    project_root: Path = field(default_factory=_project_root)

    @property
    def data_root(self) -> Path:
        return _resolve_data_root()

    @property
    def kb_dir(self) -> Path:
        return self.data_root

    @property
    def kbmd_dir(self) -> Path:
        return self.data_root / "kbmd"

    @property
    def kb_index_dir(self) -> Path:
        return self.data_root / "kb-index"

    @property
    def outputs_dir(self) -> Path:
        return self.data_root / "outputs"

    @property
    def sources_dir(self) -> Path:
        return self.data_root / "sources"

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
