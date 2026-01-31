# Pytest Subprocess Tests

Minimal end-to-end tests that run the CLI as a subprocess.

## Prerequisites

- Python 3.13+ and pip
- Install deps: `pip install -r requirements.txt`

## Build the binary

- macOS/Linux: `pyinstaller --onefile main.py --name gitmastery`
- Windows (PowerShell): `pyinstaller --onefile main.py --name gitmastery`

Binary output: `dist/gitmastery` (or `dist/gitmastery.exe` on Windows).

## Run the tests

- Go to home directory: `cd ../..`
- Use the binary: `GITMASTERY_BINARY=./dist/gitmastery python -m pytest tests/pytest-subprocess/`
