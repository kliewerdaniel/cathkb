#!/usr/bin/env bash
# Build macOS universal binary
set -euo pipefail
cd "$(dirname "$0")/.."
pip install pyinstaller
pyinstaller --onefile --name cathkb kb_tools/cli/main.py
echo "Binary: dist/cathkb"
