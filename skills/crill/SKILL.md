---
name: crill
description: Help an agent operate the public crill binary with a human in the loop. Use when installing or upgrading crill, logging into the access gate, recovering from Appium/Xcode/signing/device trust failures, or translating runtime errors into the smallest next human action plus the exact resume command.
---

# Crill

Use this skill when `crill` was installed from the public binary distribution,
not from a private source checkout.

## Detect State

1. Read the live machine state first:

```bash
crill doctor --json
```

2. Treat the machine as a first-run install target only when both are true:

- `sections.home[]` contains `home.session.json` with `status: "warn"` and
  `detail: "absent"`
- `~/.crill/device-state.json` does not exist yet

3. If the machine already has a session and a saved iOS device, skip straight
   to app resolution. Do not repeat install or login just because this file is
   a first-run orchestrator.

## First-Run Path

1. If there is no operator session yet, stop and tell the user exactly:

```bash
Run `crill auth login <email>` in your terminal first, then call this skill again.
```

Do not try to perform interactive login inside the skill. The operator must
run the terminal command themselves and follow the current CLI prompt flow.

2. If a session exists but no iOS device has been selected yet, run:

```bash
crill setup --ios
```

3. If `setup --ios` blocks on a human-only step, stop with the four-line
   contract below. Do not pad it with extra prose.

## Steady-State Path

1. Ask the participant: `What app are we testing?`
2. Resolve that answer against installed apps:

```bash
crill ios apps --json
```

3. Match the participant's reply against app names first, then bundle ids.
   If exactly one match is plausible, confirm the bundle id with the user
   before running anything. If zero or multiple matches remain, ask again.

4. Run the first narrow scan:

```bash
crill scan <bundle-id> --platform ios --max-actions 10 --max-states 10
```

5. Use the final `Output: .../scenario.yaml` line from scan output as the run
   artifact pointer. The report target is the parent run directory:

```bash
crill report runs/<timestamp>/
```

6. The golden path for this skill is `scan -> report`. `crill runs audit` is
   optional maintainer follow-up, not part of the default participant path.

## Human-Only Stop Contract

When one of the following blockers appears, stop and report exactly four
lines:

1. what is blocked
2. why `crill` or the skill cannot do it itself
3. the exact human action required
4. the exact resume command

Human-only blockers to treat this way:

- macOS `sudo` password prompts
- Apple ID password or 2FA inside `xcodes` / Xcode install flow
- iPhone "Trust This Computer?" prompt
- iPhone developer certificate trust in `Settings -> General -> VPN & Device Management`
- keeping the iPhone awake and unlocked during setup or scan

## Recovery Rules

1. Prefer current binary output over stale memory.
2. Keep human asks minimal and one step at a time.
3. Always include the exact resume command.
4. Use [references/ios-real-device.md](references/ios-real-device.md) only
   after reading the current `crill` output and error text.

## What is not gated

- `crill --help`
- `crill --version`
- `crill commands --json`
- `crill doctor`
- `crill uninstall`
- `crill ios apps`
- `crill skills install`
- `crill auth ...`
- `crill provider ...`

## Installing This Skill

```bash
crill skills install
```
