---
name: crill
description: Help an agent operate the public crill binary with a human in the loop. Use when installing or upgrading crill, logging into the access gate, recovering from Appium/Xcode/signing/device trust failures, or translating runtime errors into the smallest next human action plus the exact resume command.
---

# Crill

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

## Recovery Rules

1. Prefer current binary output over stale memory.
2. Keep human asks minimal and one step at a time.
3. Always include the exact resume command.
4. Use [references/ios-real-device.md](references/ios-real-device.md) only
   after reading the current `crill` output and error text.

## What is not gated

- `crill --help`
- `crill --version`
- `crill doctor`
- `crill uninstall`
- `crill auth ...`
- `crill provider ...`

## Installing This Skill

```bash
crill skills install
```
