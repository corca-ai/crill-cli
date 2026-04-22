# Crill Onboarding Contract

This file is the shared first-run contract for:

- the install prompt that starts from `docs/install.md`
- the public `crill` skill after the operator opens a new agent session

Keep this file honest and phase-based. The agent should inspect live state,
skip phases that are already complete, and resume from the first incomplete
phase instead of replaying the whole script every time.

## Phase 1 — Operator Session

Goal: a live `crill` gate session exists for the operator.

Read the current state first:

```bash
crill doctor --json
```

Completion rule: `gate.session` from `crill doctor --json` must be `ok`.

If `gate.reachable` is `fail`, or `gate.session.extra.reason` is
`gate_unreachable` / `server_unreachable`, stop on the gate/network problem.
Do not tell the operator to log in again yet. Ask them to restore gate reachability,
then resume with:

```bash
crill doctor --json
```

When `gate.session` is missing, invalid, or bound to a different gate, stop
and tell the user exactly:

```bash
Run `crill auth login <email>` in your terminal first, then continue from this onboarding contract.
```

For `@corca.ai` addresses, login should succeed without an invitation key.

## Phase 2 — Provider Ready

Goal: one preferred provider is chosen and persisted for future scans.

Inspect available auth sources:

```bash
crill provider status --json
```

Rules:

0. If `providers.default` from `crill doctor --json` is already `ok`, keep it
   and continue, unless the immediately previous first scan failed on the first
   LLM decision. In that failure case, re-enter Phase 2 and require a fresh
   provider recovery step instead of trusting the saved default again.

1. If exactly one provider is clearly available, tell the operator which one
   was detected and persist it:

```bash
crill config provider set <provider>
```

2. If multiple providers are available, ask the operator which one to use for
   this trial, then persist that answer:

```bash
crill config provider set <provider>
```

3. If no provider is available, stop with the four-line human-only contract and
   ask the operator to log into exactly one supported provider path first.

Do not give a broad provider menu when none are configured. Prefer the host CLI
the operator is already using:

- Claude Code host -> `claude auth login`
- Codex host -> `codex login`
- Gemini host -> `gemini` auth / OAuth setup

After the operator completes that one provider login, resume by persisting the
chosen provider explicitly:

```bash
crill config provider set <provider>
```

Then continue to the next incomplete onboarding phase.

The saved provider becomes the default for future scans unless a pool or an
explicit `--provider` flag overrides it.

## Phase 3 — iOS Device Setup

Goal: one real iOS device is selected, connected, and not obviously blocked on
host-side signing/provider readiness.

Completion rule: `home.saved-ios-device` from `crill doctor --json` must be `ok`.
This proves the saved device is still connected and signing/provider readiness
looks plausible; it does not replace `crill setup --ios` if later app listing
or scan output shows a real Appium/WDA/trust blocker.

If no saved iOS device is present yet, or the saved one is no longer connected,
run:

```bash
crill setup --ios
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
- keeping the iPhone awake and unlocked during setup or scan

## Phase 4 — Target App Resolution

Goal: the trial app is explicitly chosen for this session.

Ask the participant:

`What app are we testing?`

Resolve that answer against installed iOS apps:

```bash
crill ios apps --json
```

Match by app name first, then bundle id. If exactly one match is plausible,
confirm the bundle id before scanning. If zero or multiple matches remain, ask
again instead of guessing.

## Phase 5 — First-Run Preset Confirmation

Goal: the first scan stays intentionally narrow.

Use this fixed preset for the first internal iOS run:

- one iPhone
- one app
- saved default provider from Phase 2
- `--max-actions 10 --max-states 10`
- no diff, no audit gate, no broad telemetry budget

Before running the scan, say the plan in one compact confirmation:

`I will scan <bundle-id> on iOS with provider <provider> using the first-run preset (max-actions 10, max-states 10). Continue?`

## Phase 6 — First Scan And Report

Run the first scan with the fixed preset:

```bash
crill scan <bundle-id> --platform ios --max-actions 10 --max-states 10
```

Use the final `Output: .../scenario.yaml` line as the run artifact pointer.
The report target is the parent run directory:

```bash
crill report runs/<timestamp>/
```

The golden path is `scan -> report`. `crill runs audit` is maintainer
follow-up, not part of the participant default path.

If the first LLM decision fails, stop and return to provider recovery instead
of letting the scan continue with blind back-navigation. Do not trust the
existing `providers.default == ok` row alone after that failure; require a
fresh provider recovery step first.

## Recovery Rules

1. Prefer current `crill` output over stale memory.
2. Skip completed phases and resume from the first incomplete one.
3. Keep human asks minimal and one step at a time.
4. Always include the exact resume command.
5. Use `ios-real-device.md` only after reading the live error text.
6. When the operator needs to invoke the skill manually, use the form their
   host expects. Typical examples are `/crill` in Claude Code and `$crill` in
   Codex, but prefer the host's own guidance over stale memory.
