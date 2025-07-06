# app

Git-Mastery CLI to centralize and perform key operations of adapters

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

A Github Actions workflow exists to automatically publish the changes to Homebrew.

Linux packaging is performed to Debian and Arch based distros. Notes can be
[found here.](https://woojiahao.notion.site/linux-packaging-226f881eda0580d68bc8dc6f8e1d5d0d?source=copy_link)
