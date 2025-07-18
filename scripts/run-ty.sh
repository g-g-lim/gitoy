#!/bin/bash
# Script to run ty type checking with proper PATH setup
# This ensures uvx is available even when run from VSCode

# Add common uvx installation paths
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"
export PATH="/usr/local/bin:$PATH"

# Try to find uvx
if command -v uvx >/dev/null 2>&1; then
    uvx ty check "$@"
    uvx ruff check "$@"
else
    echo "Error: uvx not found in PATH"
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi 