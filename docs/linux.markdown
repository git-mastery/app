---
layout: page
title: Linux
---

## Git

### Verification

Check if Git is already installed:

```bash
git version
```

If you see something like `git version 2.48.1`, Git is already installed.

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


## Git-Mastery

### Debian/Ubuntu

Ensure you are running `libc` version 2.38 or newer.

Then install the following:

```bash
sudo apt install software-properties-common
sudo add-apt-repository "deb https://git-mastery.github.io/gitmastery-apt-repo any main"
sudo apt update
sudo apt-get install gitmastery
```

### Arch

Install using pacman:

```bash
sudo pacman -Syu gitmastery-bin
```

### Others

If you are using a Linux distribution that is not yet supported by Git-Mastery, please download the right binary for your architecture from [the latest release.](https://github.com/git-mastery/app/releases/latest)

Install it to `/usr/bin` to access the binary, the following using version `3.3.0` as an example.

```bash
install -D -m 0755 gitmastery-3.3.0-linux-arm64 /usr/bin/gitmastery
```

## GitHub

### Create Account

Create a [new GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) if needed.

### SSH Setup

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

Refer to the [GitHub CLI Linux installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) for your distribution.

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

Verify that Github and Github CLI is setup for Git-Mastery:

```bash
gitmastery check github
```
