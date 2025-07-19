# app

Git-Mastery CLI to centralize and perform key operations of adapters

## OS support

We currently support:

1. Windows `.exe` (amd64)
2. MacOS Homebrew  (arm64)
3. Debian `.deb` and APT (amd64 and arm64)
4. Arch AUR (amd64)

If you wish to contribute to the packaging support, file a PR!

## Installation

### Windows

1. Download the `.exe` from the [latest release](https://github.com/git-mastery/app/releases/latest).
2. Add the `.exe` to your `PATH`

### MacOS

1. Add the Homebrew tap: `brew tap git-mastery/gitmastery`
2. Install the package: `brew install gitmastery`

### Debian-based distros

1. Install `add-apt-repository`: `sudo apt update && sudo apt-get install software-properties-common`
2. Add the `gitmastery-apt-repo` repository: `sudo add-apt-repository "deb https://git-mastery.github.io/gitmastery-apt-repo any main"`
3. Install the package: `sudo apt update && sudo apt-get install gitmastery`

### Arch-based distros

1. Install the package: `sudo pacman -Syu gitmastery-bin`

## Local development

To develop the app locally, create a virtualenv and download the requirements to start.

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
