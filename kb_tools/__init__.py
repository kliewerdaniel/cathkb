"""Catholic Sovereign Knowledge System — Core Package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cathkb")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
