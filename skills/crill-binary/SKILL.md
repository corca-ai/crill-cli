---
name: crill-binary
description: Use when operating the public crill binary install. It covers Homebrew install or upgrade, gate login, doctor-based diagnostics, and the smallest next command to resume after a failure.
---

# Crill Binary

Use this skill when `crill` was installed from the public binary distribution,
not from a private source checkout.

## Core flow

1. Install or upgrade:

```bash
brew install corca-ai/tap/crill
brew upgrade crill
```

2. Verify the install:

```bash
crill --version
crill doctor
```

3. Log in before any gated work:

```bash
crill auth login <email>
crill auth whoami
```

4. Run the actual workflow only after login succeeds:

```bash
crill setup --ios
crill scan --platform ios
```

## What is not gated

These commands should remain usable even when login is broken:

- `crill --help`
- `crill --version`
- `crill doctor`
- `crill uninstall`
- `crill auth ...`
- `crill provider ...`

## Recovery

- Start with `crill doctor`.
- If the gate rejects the session, rerun `crill auth login <email>`.
- If a human step is required, say what is blocked, why automation cannot finish
  it, the exact action required, and the exact resume command.
