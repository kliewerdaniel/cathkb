#!/usr/bin/env bash
# Catholic Sovereign Knowledge System — Bootstrap Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════╗"
echo "║  Catholic Sovereign Knowledge System — Setup     ║"
echo "╚══════════════════════════════════════════════════╝"

# ── 1. Create directory structure ──────────────────────────
echo ""
echo "▸ Creating directory structure..."
mkdir -p kb_tools/{cli,web,web/templates,web/static,mcp,search,reasoning,ingest,index}
mkdir -p tests/{unit,integration,acceptance}
mkdir -p scripts
mkdir -p data/outputs/{study-guides,timelines,comparisons,doctoral-briefs}
mkdir -p data/sources/{raw,normalized}
mkdir -p .github/workflows

# ── 2. Create __init__.py files ────────────────────────────
echo "▸ Creating package files..."
for dir in kb_tools kb_tools/cli kb_tools/web kb_tools/mcp kb_tools/search kb_tools/reasoning kb_tools/ingest kb_tools/index tests tests/unit tests/integration tests/acceptance; do
    touch "$dir/__init__.py"
done

# ── 3. Copy .env if not present ────────────────────────────
if [ ! -f .env ]; then
    echo "▸ Creating .env from .env.example..."
    cp .env.example .env
    echo "  ✓ Edit .env to configure your environment"
else
    echo "▸ .env already exists, skipping"
fi

# ── 4. Create virtual environment ──────────────────────────
echo "▸ Setting up Python virtual environment..."
if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "  ✓ Created .venv"
else
    echo "  ✓ .venv already exists"
fi

# ── 5. Install dependencies ────────────────────────────────
echo "▸ Installing dependencies..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -e ".[dev]"
echo "  ✓ Dependencies installed"

# ── 6. Verify Ollama ──────────────────────────────────────
echo "▸ Checking Ollama..."
if command -v ollama &>/dev/null; then
    if ollama list 2>/dev/null | grep -q "qwen2.5-coder"; then
        echo "  ✓ qwen2.5-coder:32b model available"
    else
        echo "  ⚠ qwen2.5-coder:32b not found — run: ollama pull qwen2.5-coder:32b"
    fi
    if ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
        echo "  ✓ nomic-embed-text model available"
    else
        echo "  ⚠ nomic-embed-text not found — run: ollama pull nomic-embed-text"
    fi
else
    echo "  ⚠ Ollama not found — install from https://ollama.com"
fi

# ── 7. Run linter ─────────────────────────────────────────
echo "▸ Running linter..."
.venv/bin/ruff check kb_tools/ --quiet 2>/dev/null && echo "  ✓ Lint clean" || echo "  ⚠ Lint issues found"

# ── 8. Run tests ──────────────────────────────────────────
echo "▸ Running tests..."
if .venv/bin/pytest tests/ --quiet --tb=no 2>/dev/null; then
    echo "  ✓ Tests pass"
else
    echo "  ⚠ Some tests failed (expected if data not fully loaded)"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Setup complete!                                 ║"
echo "║                                                  ║"
echo "║  Next steps:                                     ║"
echo "║    1. Activate venv:  source .venv/bin/activate  ║"
echo "║    2. Query:          cathkb query '...'         ║"
echo "║    3. Web UI:         cathkb serve               ║"
echo "║    4. Build index:    cathkb build               ║"
echo "╚══════════════════════════════════════════════════╝"
