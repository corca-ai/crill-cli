# crill install

This document is for an agent driving a first internal iOS `crill` setup with
a human in the loop. Keep this file thin: install the public binary, get a
session, install the public skill, then hand off to the installed skill's
shared onboarding contract for the actual setup and first scan.

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

The installed public `crill` skill now includes a shared onboarding reference
at `references/onboarding.md`.

Now close this agent session. Open a new one, invoke the `crill` skill, and
have it read its own `references/onboarding.md` before it continues. That
reference owns provider selection, iOS setup, app resolution, the first-run
scan preset, and the first `scan -> report` flow.

Use the skill-invocation form your current host expects. Typical examples are
`/crill` in Claude Code and `$crill` in Codex, but prefer the host's own skill
or slash-command guidance over hardcoded memory.

## Human-Only Steps

If the agent stops on one of these, the human must handle it directly:

- macOS `sudo` password prompts
- Apple ID password or 2FA during Xcode install
- iPhone "Trust This Computer?" prompt
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- Keeping the iPhone awake and unlocked during setup or scan
