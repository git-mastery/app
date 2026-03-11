#!/bin/bash
# Build and run E2E tests for gitmastery

set -e
FILENAME="gitmastery"

echo "Building gitmastery binary..."
pyinstaller --onefile main.py --name $FILENAME

echo "Running E2E tests..."
pytest tests/e2e -v

echo "All E2E tests passed!"
