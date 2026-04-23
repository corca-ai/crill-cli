# Crill Onboarding Contract

This file no longer owns a separate phase checklist. The source of truth for
the next onboarding step is:

```bash
crill doctor --next-action
```

## Core Loop

1. Run `crill doctor --next-action`.
2. If it returns a command, run that command exactly.
3. After the command finishes, run `crill doctor --next-action` again.
4. Repeat until doctor says the machine is ready for the first iOS scan.

The readiness gates behind that loop are still:

- `gate.session`
- `providers.default`
- `home.saved-ios-device`

That last row currently also covers the supported simulator path even though
the row name still says "device".

## Gate and Provider Recovery

If doctor points at gate-session recovery, use:

```bash
crill auth login <email>
```

If doctor points at provider recovery and exactly one provider is already
available, persist it:

```bash
crill config provider set <provider>
```

If doctor says no provider is currently available, sign into exactly one
supported provider path first, then rerun `crill doctor --next-action`.

Examples:

- Claude Code host -> `claude auth login`
- Codex host -> `codex login`
- Gemini host -> `gemini` auth / OAuth setup

## iOS Init Recovery

If doctor points at iOS environment repair, run:

```bash
crill init ios
```

If this blocks on a human-only step, stop with:

1. what is blocked
2. why `crill` or the skill cannot do it itself
3. the exact human action required
4. the exact resume command

Human-only blockers include:

- macOS `sudo` password prompts
- Apple ID password or 2FA inside the Xcode install flow
- iPhone `Trust This Computer?` prompt
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- keeping the iPhone awake and unlocked during init or scan

## Ready For First Scan

When doctor says the machine is ready, resolve the target app next:

```bash
crill ios apps --json
```

Ask the participant:

`What app are we testing?`

Match by app name first, then bundle id. If exactly one match is plausible,
confirm the bundle id before scanning. If zero or multiple matches remain, ask
again instead of guessing.

Run the first quick-check scan:

```bash
crill scan <bundle-id> --platform ios --max-actions 10 --max-states 10
crill report runs/<timestamp>/
```

If the first LLM decision fails, return to provider recovery instead of
trusting the saved provider state blindly.

When the operator needs to invoke the installed skill manually, use the form
their host expects. Typical examples are `/crill` in Claude Code and `$crill`
in Codex, but prefer the host's own guidance over stale memory.
