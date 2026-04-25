#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing / verifying dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "Starting Group Dynamics Simulator at http://localhost:8000"
echo "Press Ctrl+C to stop."
echo ""
python run.py
