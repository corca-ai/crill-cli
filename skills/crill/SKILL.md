---
name: crill
description: Help an agent operate the public crill binary with a human in the loop. Use when installing or upgrading crill, logging into the access gate, recovering from agent-device/Xcode/signing/device trust failures, or translating runtime errors into the smallest next human action plus the exact resume command.
---

# Crill

Use this skill when `crill` was installed from the public binary distribution,
not from a private source checkout.

Read and follow [`references/onboarding.md`](references/onboarding.md) first.
That file points back to `crill doctor --next-action` as the source of truth
for the next onboarding step. Do not invent a parallel setup script in chat.

If the operator needs to invoke this skill manually, use the form their host
expects. Typical examples are `/crill` in Claude Code and `$crill` in Codex,
but prefer the host's own skill-invocation guidance over stale memory.

## State Detection

1. Read the live machine state first:

```bash
crill doctor --next-action
```

2. If the next action is an executable command, run it exactly, then rerun
   `crill doctor --next-action`.

3. If `gate.reachable` is `fail`, or `gate.session.extra.reason` is
   `gate_unreachable` / `server_unreachable`, stop on the gate/network problem
   and ask the operator to restore reachability before continuing from:

```bash
crill doctor --next-action
```

4. Keep iterating until `crill doctor --next-action` flips from recovery work
   to app resolution or first-scan readiness.

## iOS Readiness

Before the first real-device scan, run the operator-pasteable readiness
aggregator:

```bash
crill doctor --ios-readiness
```

It runs the four iOS tier-1 preflights (Developer Mode, Mac pairing, Xcode
accounts, signing) and exits non-zero if any fail. The output already follows
the four-part blocker contract — what is blocked, why crill cannot finish, the
exact human action, the exact resume command — so do not paraphrase or merge
its lines into a checklist. Have the operator paste the full output and follow
each blocker as printed, then re-run the same command until it returns a clean
pass.

A clean readiness pass is the gate before the first real-device scan.

## Provider Selection

When doctor points at provider selection, inspect the available auth sources:

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

When doctor says the machine is ready for the first scan, ask the participant:

`What app are we testing?`

Then resolve that answer against installed apps:

```bash
crill ios apps --json
```

Match by app name first, then bundle id. If exactly one match is plausible,
confirm the bundle id before scanning. If zero or multiple matches remain, ask
again instead of guessing.

## First-Run Preset

The default participant path uses one fixed quick-check preset:

```bash
crill scan <bundle-id> --platform ios --max-actions 10 --max-states 10
```

Use these participant-facing scan-depth names when discussing the next run:

- `quick check`: `--max-actions 10 --max-states 10`
- `standard exploration`: omit both flags and use the default scan limits
- `deeper exploration`: increase both flags intentionally after reviewing the first run

Before running the scan, confirm the exact plan in one compact line:

`I will scan <bundle-id> on iOS with provider <provider> using the quick-check preset. Continue?`

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
- iPhone Developer Mode toggle in `Settings -> Privacy & Security -> Developer Mode` (iOS 16+)
- iPhone `Trust This Computer?` prompt
- adding an Apple ID in `Xcode -> Settings -> Accounts` when none is configured
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- keeping the iPhone awake and unlocked during init or scan

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
