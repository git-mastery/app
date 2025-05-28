# cli

CLI for Git-Mastery to centralize and perform key operations of adapters

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Publishing

```bash
pyinstaller gitmastery.spec
git tag v*.*.*
git push --tags
```

A Github Actions workflow exists to automatically publish the changes to Homebrew (more support to come).
