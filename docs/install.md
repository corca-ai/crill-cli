# crill install

This document is for an agent driving a first internal iOS `crill` install with
a human in the loop. Keep this file thin: install the public binary, get a
session, install the public skill, then let `crill doctor --next-action`
choose the next onboarding step until the machine is ready for the first scan.

## Prerequisites

- An Apple Silicon Mac
- Either an iPhone plus USB cable, or Xcode with an available iOS simulator
- For real-device work, an Apple ID already signed in through macOS System Settings
- The target app available on the chosen iPhone or simulator

Do not pre-collect an LLM API key or invitation key for this flow. The only
required login input up front is the operator email address.

## Install The Binary

```bash
curl -sSfL https://raw.githubusercontent.com/corca-ai/crill-cli/main/install.sh | sh
crill --version
```

`install.sh` installs both the CLI bundle and the owned iOS runtime. On a
healthy fresh machine, the same step now materializes
`~/.crill/runtime.json` and `~/.crill/runtime/current/` before the first
`crill scan`.

If a later `crill doctor --next-action` reports missing or broken owned-runtime
paths, rerun the installer to restore them:

```bash
curl -sSfL https://raw.githubusercontent.com/corca-ai/crill-cli/main/install.sh | sh
```

## Gatekeeper One-Time Unblock

The current macOS binary is unsigned. If macOS blocks the first launch, open
Finder and approve the bundled binary once:

1. Open `~/.local/bin/crill.bundle/crill` in Finder. If you installed to a
   custom `INSTALL_DIR`, use `<install-dir>/crill.bundle/crill` instead.
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

Run the doctor loop:

```bash
crill doctor --next-action
```

If an agent is driving, give it this prompt:

```md
Use `crill` on this machine.
Start with `crill doctor --next-action`.
If it returns a command, run it exactly.
After each step, rerun `crill doctor --next-action` and repeat.
Stop only when doctor says the machine is ready for the first iOS scan.
Then ask me which app to test, resolve it with `crill ios apps --json`, and run one quick first scan.
If a human-only step blocks progress, stop and tell me:
1. what is blocked,
2. why you cannot do it,
3. the exact human action,
4. the exact resume command.
```

The important readiness rows behind that loop are `install.skill.global`,
`gate.session`, `providers.default`, and `home.saved-ios-device`
(which currently also covers the supported simulator path even though the row
name still says "device").

If the current host supports an installed `crill` skill, you can still invoke
it after `crill skills install`, but the source of truth for the next step is
now `crill doctor --next-action`, not a separate onboarding phase checklist.

Use the skill-invocation form your current host expects. Typical examples are
`/crill` in Claude Code and `$crill` in Codex, but prefer the host's own skill
or slash-command guidance over hardcoded memory.

## Human-Only Steps

If the agent stops on one of these, the human must handle it directly:

- macOS `sudo` password prompts
- Apple ID password or 2FA during Xcode install
- iPhone "Trust This Computer?" prompt
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- Keeping the iPhone awake and unlocked during init or scan
