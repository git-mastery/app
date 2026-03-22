#!/bin/bash
# Build and run E2E tests for gitmastery

set -e
FILENAME="gitmastery"

echo "Building gitmastery binary..."
uv run pyinstaller --onefile main.py --name $FILENAME

echo "Running E2E tests..."
uv run pytest tests/e2e -v

echo "All E2E tests passed!"
