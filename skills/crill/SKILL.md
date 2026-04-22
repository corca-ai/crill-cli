---
name: crill
description: Help an agent operate the public crill binary with a human in the loop. Use when installing or upgrading crill, logging into the access gate, recovering from Appium/Xcode/signing/device trust failures, or translating runtime errors into the smallest next human action plus the exact resume command.
---

# Crill

Use this skill when `crill` was installed from the public binary distribution,
not from a private source checkout.

Read and follow [`references/onboarding.md`](references/onboarding.md) first.
That file is the shared onboarding contract for both the install prompt and
this skill. Do not invent a parallel setup script in chat.

If the operator needs to invoke this skill manually, use the form their host
expects. Typical examples are `/crill` in Claude Code and `$crill` in Codex,
but prefer the host's own skill-invocation guidance over stale memory.

## State Detection

1. Read the live machine state first:

```bash
crill doctor --json
```

2. Use the onboarding contract phases to decide what is already complete and
   what still needs work. Treat these rows as the phase gates:

- `gate.session` must be `ok`
- `providers.default` must be `ok`
- `home.saved-ios-device` must be `ok`

Skip completed phases and resume from the first incomplete phase.

3. If `gate.reachable` is `fail`, or `gate.session.extra.reason` is
   `gate_unreachable` / `server_unreachable`, stop on the gate/network problem
   and ask the operator to restore reachability before continuing from:

```bash
crill doctor --json
```

4. If `gate.session` is not `ok` for missing or stale-session reasons, tell
   the user exactly:

```bash
Run `crill auth login <email>` in your terminal first, then continue from this onboarding contract.
```

Do not try to perform interactive login inside the skill.

## Provider Selection

When the onboarding contract reaches provider selection, inspect the available
auth sources:

```bash
crill provider status --json
```

If `providers.default` is already `ok`, keep it and continue unless the
immediately previous first scan failed on the first LLM decision. In that
failure case, re-run provider recovery instead of trusting the saved default
again.

If exactly one provider is available, say which one was detected and persist it:

```bash
crill config provider set <provider>
```

If multiple providers are available, ask once which one to use for this trial,
then persist that answer with the same command.

If no provider is available, stop with one concrete provider path, not a vague
list. Prefer the host CLI the operator is already using:

- Claude Code host -> `claude auth login`
- Codex host -> `codex login`
- Gemini host -> `gemini` auth / OAuth setup

Then give the exact resume command:

```bash
crill config provider set <provider>
```

## Target App Resolution

When the onboarding contract reaches app resolution, ask the participant:

`What app are we testing?`

Then resolve that answer against installed apps:

```bash
crill ios apps --json
```

Match by app name first, then bundle id. If exactly one match is plausible,
confirm the bundle id before scanning. If zero or multiple matches remain, ask
again instead of guessing.

## First-Run Preset

The default participant path uses one fixed first-run preset:

```bash
crill scan <bundle-id> --platform ios --max-actions 10 --max-states 10
```

Before running the scan, confirm the exact plan in one compact line:

`I will scan <bundle-id> on iOS with provider <provider> using the first-run preset (max-actions 10, max-states 10). Continue?`

Use the final `Output: .../scenario.yaml` line from scan output as the run
artifact pointer. The report target is the parent run directory:

```bash
crill report runs/<timestamp>/
```

## Human-only blockers

When one of the following blockers appears, stop and report exactly four
lines:

1. what is blocked
2. why `crill` or the skill cannot do it itself
3. the exact human action required
4. the exact resume command

Human-only blockers to treat this way:

- macOS `sudo` password prompts
- Apple ID password or 2FA inside `xcodes` / Xcode install flow
- iPhone `Trust This Computer?` prompt
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- keeping the iPhone awake and unlocked during setup or scan

## Recovery rules

1. Prefer current binary output over stale memory.
2. Keep human asks minimal and one step at a time.
3. Always include the exact resume command.
4. Use [`references/ios-real-device.md`](references/ios-real-device.md) only
   after reading the current `crill` output and error text.
5. If the first LLM decision fails during the first scan, stop and return to
   provider recovery instead of letting the scan drift. Do not trust
   `providers.default == ok` alone after that failure.

## What is not gated

- `crill --help`
- `crill --version`
- `crill commands --json`
- `crill doctor`
- `crill uninstall`
- `crill ios apps`
- `crill auth ...`
- `crill provider ...`
- `crill config provider ...`
- `crill skills install`

## Installing This Skill

```bash
crill skills install
```
