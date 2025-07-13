---
layout: page
title: MacOS
---

## Homebrew

Homebrew is a package manager for macOS that makes installing development tools much easier. Most of the tools in this guide can be installed using Homebrew.

### Verification

Check if Homebrew is already installed:

```bash
brew --version
```

If you see output like `Homebrew 4.x.x`, Homebrew is installed and you can skip to the Git section.

### Installation

Install Homebrew by running this command in Terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Git

### Verification

Check if Git is already installed:

```bash
git version
```

If you see output like `git version 2.48.1`, Git is installed and you can skip to the GitHub section.

### Installation

Install Git using Homebrew:

```bash
brew install git
```

### Git Configuration

After installing Git, you need to configure it with your identity and preferences.

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

## GitHub

### Create Account

Create a [new GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) if you don't have one.

### SSH Setup

#### 1. Check for Existing SSH Keys

```bash
ls -al ~/.ssh
```

Look for files named `id_rsa.pub`, `id_ecdsa.pub`, or `id_ed25519.pub`. If you have one, skip to step 4.

#### 2. Create New SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
Press Enter to accept all defaults (including empty passphrase).

#### 3. Add SSH Key to ssh-agent

Start the ssh-agent:

```bash
eval "$(ssh-agent -s)"
```

Configure SSH (for macOS Sierra 10.12.2 or later):

```bash
touch ~/.ssh/config
```

Add this to your `~/.ssh/config` file:

```
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

Add your SSH key:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

#### 4. Add SSH Key to GitHub

Copy your public key to clipboard:

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

1. Go to GitHub → Settings → SSH and GPG keys → New SSH key
2. Give it a name and paste your public key
3. Save

#### 5. Verify SSH Connection

```bash
ssh -T git@github.com
```

Type `yes` when prompted, and you should see a message with your username.

## GitHub CLI

### Installation

With Homebrew installed, installing GitHub CLI is simple:

```bash
brew install gh
```

### Authentication

```bash
gh auth login
```

Select SSH when prompted (since you set up SSH above).

### Verification

```bash
gh auth status
```

You should see confirmation that you're logged in with SSH protocol.

