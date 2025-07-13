---
layout: page
title: Windows (Git Bash)
---

## Git

### Verification

Check if Git is already installed:

```bash
git version
```

If you see output like `git version 2.48.1`, Git is installed and you can skip to the GitHub section.

### Installation

Download the Git installer from the [official Git website](https://git-scm.com/downloads/win).  
Run the installer and make sure to select the option to install **Git Bash** when prompted.

### Git Configuration

After installing Git, configure your identity and preferences:

#### Set Your Name

```bash
git config --global user.name "Your Name"
```

You can use a pseudonym if you want to keep your real name private.

#### Set Your Email

```bash
git config --global user.email "your_email@example.com"
```

To keep your email private, GitHub offers a `noreply` email. Set this up by going to:

1. GitHub → Settings → Emails
2. Enable **"Keep my email address private"**
3. Use the provided `username@users.noreply.github.com`

#### Set Default Branch Name

```bash
git config --global init.defaultBranch main
```

## Git-Mastery

1. Download the `.exe` file from [the latest release](https://github.com/git-mastery/app/releases/latest).
2. Add the `.exe` to your `PATH` following [this guide](https://www.eukhost.com/kb/how-to-add-to-the-path-on-windows-10-and-windows-11/).

## GitHub

### Create Account

Create a [new GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) if you don't have one.

### SSH Setup

#### 1. Check for Existing SSH Keys

```bash
ls -al ~/.ssh
```

Look for files like `id_ed25519.pub`.

#### 2. Create New SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### 3. Add SSH Key to ssh-agent

In a **PowerShell (Admin)** window:

```powershell
Get-Service -Name ssh-agent | Set-Service -StartupType Manual
Start-Service ssh-agent
ssh-add ~/.ssh/id_ed25519
```

#### 4. Add SSH Key to GitHub

Copy your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Then add it to GitHub → Settings → SSH and GPG Keys.

#### 5. Verify SSH Connection

```bash
ssh -T git@github.com
```

Say `yes` when prompted, and you should see a welcome message with your username.

## GitHub CLI

### Installation

Download the `.msi` installer from the [GitHub CLI releases page](https://github.com/cli/cli/releases).

### Authentication

```bash
gh auth login
```

Choose SSH when prompted.

### Verification

```bash
gh auth status
```

You should see confirmation that you're logged in with SSH protocol.

Verify that Github and Github CLI is setup for Git-Mastery:

```bash
gitmastery check github
```
