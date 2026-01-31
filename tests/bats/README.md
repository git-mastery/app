# BATS Automated Tests

This directory contains BATS (Bash Automated Testing System) tests for the GitMastery binary. These tests are designed to validate the functionality of the compiled binary in a shell environment.

## Prerequisites

- BATS (see the [BATS GitHub repository](https://github.com/bats-core/bats-core))
- Python 3.13+ and pip
- Install deps: `pip install -r requirements.txt`

## Build the binary

- macOS/Linux: `pyinstaller --onefile main.py --name gitmastery`
- Windows (PowerShell): not supported for BATS tests.

Binary output: `dist/gitmastery`.

## Run the tests

- Go to home directory: `cd ../..`
- `GITMASTERY_BINARY=./dist/gitmastery bats tests/bats` to run the specific built binary.
