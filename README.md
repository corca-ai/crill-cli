# Crill CLI

Public binary distribution and operator-facing usage skill for `crill`.

This repository intentionally does **not** contain product source code. The
private source of truth lives in `corca-ai/crill`. This repo exists so binary
artifacts can be downloaded anonymously by Homebrew and other installer flows.

## Install

```bash
brew install corca-ai/tap/crill
```

## Access Control

Installing the binary is public. Using gated product commands is not.

- `crill auth login <email>` exchanges an invitation for a session token.
- Gated commands fail until the operator logs in successfully.
- Ungated commands remain available for inspection and recovery:
  `crill --help`, `crill --version`, `crill doctor`, `crill uninstall`,
  `crill auth ...`, `crill provider ...`

## Latest Public Release

- Version: `0.2.2`
- Release: `https://github.com/corca-ai/crill-cli/releases/tag/v0.2.2`
- Source release mirrored from: `https://github.com/corca-ai/crill/releases/tag/v0.2.2`

## Skill

The public usage skill lives under [`skills/crill-binary`](skills/crill-binary).
