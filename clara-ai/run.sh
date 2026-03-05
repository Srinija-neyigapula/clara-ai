#!/usr/bin/env bash
# run.sh – Quick launcher for the Clara AI pipeline.
# Usage: ./run.sh

set -e

echo "======================================================"
echo "  Clara AI Pipeline – Zero-Cost Automation"
echo "======================================================"

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON=python3
# Prefer python if it's already Python 3
if command -v python &>/dev/null; then
    PY_VER=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
    if [ "$PY_VER" = "3" ]; then
        PYTHON=python
    fi
fi

$PYTHON run.py

echo ""
echo "Done! Check the outputs/ directory for results."
