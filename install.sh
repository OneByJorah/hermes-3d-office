#!/bin/bash
set -e

echo "🖥  Hermes 3D Office installer"

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
fi

python3 -m pip install --user -r requirements.txt 2>/dev/null || echo "No Python deps required."

echo ""
echo "🚀 Start the dashboard:"
echo "   cd $REPO_DIR"
echo "   python3 server.py"
echo ""
echo "Then open http://localhost:9502"
echo "Edit .env to wire your Hermes Agent API."
