---
layout: page
title: Windows (WSL)
---

We recommend using WSL over Git Bash for Git-Mastery on Windows.

## WSL Installation

To get started with Windows Subsystem for Linux (WSL), you'll need to enable the feature and install a Linux distribution.

### Enable WSL

Open PowerShell or Windows Command Prompt as an administrator and run the following command:

```ps1
wsl --install
```

This command will enable the necessary optional components, download the latest Linux kernel, set WSL 2 as your default, and install **Ubuntu** by default. Ubuntu is generally recommended for its wide community support and extensive package availability.

```ps1
wsl --install -d Ubuntu-24.04
```

If you want to install a different distribution, you can specify it:

```ps1
wsl --install -d <distribution name>
```

Once installed, launch the distribution from the Start Menu. The first time you launch it, you'll be prompted to create a username and password for your new Linux environment.

## Git

### Verification

Check if Git is already installed within your WSL distribution:

```bash
git version
```

If you see something like `git version 2.48.1`, Git is already installed.

### Installation

If Git is not installed, follow the instructions for your specific WSL distribution:

#### Ubuntu

```bash
sudo apt update
sudo apt install git
```

#### Arch

```bash
sudo pacman -Syu git
```

### Git Configuration

After installing Git, you need to configure it with your identity and preferences. These configurations will be specific to your WSL environment.

#### Set Your Name

Set the name that will be associated with your Git commits:

```bash
git config --global user.name "Your Name"
```

You can use any name you want if you wish to keep your real name private. This name will be visible in commit history on GitHub.

#### Set Your Email

Set the email address for your commits:

```bash
git config --global user.email "your_email@example.com"
```

If you want to keep your email private, GitHub provides a special `noreply` email address. You can set yours up after you setup Github.

You can find yours by:

1. Going to GitHub → Settings → Emails
2. Looking for "Keep my email addresses private"
3. Using the provided `noreply` email address (format: `username@users.noreply.github.com`)

#### Set Default Branch Name

Configure Git to use `main` as the default branch name for new repositories:

```bash
git config --global init.defaultBranch main
```

## Git-Mastery

Follow the installation instructions for your specific WSL distribution, as Git-Mastery will be installed directly within your Linux environment.

### Ubuntu

Ensure you are running `libc` version 2.38 or newer.

Then install the following:

```bash
echo "deb [trusted=yes] https://git-mastery.org/gitmastery-apt-repo any main" | \
  sudo tee /etc/apt/sources.list.d/gitmastery.list > /dev/null
sudo apt install software-properties-common
sudo add-apt-repository "deb https://git-mastery.org/gitmastery-apt-repo any main"
sudo apt update
sudo apt-get install gitmastery
```

### Arch

Install using `pacman`:

```bash
sudo pacman -Syu gitmastery-bin
```

### Others

If you are using a Linux distribution in WSL that is not yet supported by Git-Mastery, please download the right binary for your architecture from [the latest release.](https://github.com/git-mastery/app/releases/latest)

Install it to `/usr/bin` to access the binary, the following using version `3.3.0` as an example.

```bash
install -D -m 0755 gitmastery-3.3.0-linux-arm64 /usr/bin/gitmastery
```

## GitHub

### Create Account

Create a [new GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) if needed.

### SSH Setup

Perform these steps within your WSL distribution.

#### 1. Check for Existing SSH Keys

```bash
ls -al ~/.ssh
```

Look for `id_ed25519.pub` or similar.

#### 2. Create New SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept all defaults.

#### 3. Add SSH Key to ssh-agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

#### 4. Add SSH Key to GitHub

```bash
cat ~/.ssh/id_ed25519.pub
```

Paste the output into GitHub → Settings → SSH and GPG Keys.

#### 5. Verify SSH Connection

```bash
ssh -T git@github.com
```

## GitHub CLI

### Installation

Refer to the [GitHub CLI Linux installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) for your specific WSL distribution (Ubuntu or Arch).

### Authentication

```bash
gh auth login
```

Choose **SSH** when prompted.

### Verification

```bash
gh auth status
```

You should see confirmation of your GitHub login using SSH.

Verify that Github and GitHub CLI is setup for Git-Mastery:

```bash
gitmastery check github
```

