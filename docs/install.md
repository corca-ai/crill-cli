# crill install

This document is for an agent driving a first internal iOS `crill` setup with
a human in the loop. Keep this file thin: install the public binary, get a
session, install the public skill, then hand off to that skill for the actual
device setup and first scan.

## Prerequisites

- A Mac
- An iPhone plus USB cable
- Homebrew
- An Apple ID already signed in through macOS System Settings
- The target app already installed on the iPhone

Do not pre-collect an LLM API key or invitation key for this flow. The only
required login input up front is the operator email address.

## Install The Binary

```bash
brew install corca-ai/tap/crill
crill --version
```

## Gatekeeper One-Time Unblock

The current macOS binary is unsigned. If macOS blocks the first launch, open
Finder and approve the binary once:

1. Open `/opt/homebrew/bin/crill` on Apple Silicon, or `/usr/local/bin/crill`
   on Intel Macs.
2. Right-click, choose **Open**, and confirm once.
3. Return to the terminal and run `crill` normally.

## Sign In

```bash
crill auth login <email>
```

For `@corca.ai` addresses, `crill` should sign in without asking for an
invitation key. Other domains may still be prompted for one by the CLI.

## Install The Public Skill

```bash
crill skills install
```

## Next Step

Now close this agent session. Open a new one and invoke the `crill` skill. It
will drive the remaining setup, app resolution, first scan, and report flow.

## Human-Only Steps

If the agent stops on one of these, the human must handle it directly:

- macOS `sudo` password prompts
- Apple ID password or 2FA during Xcode install
- iPhone "Trust This Computer?" prompt
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- Keeping the iPhone awake and unlocked during setup or scan
