# Crill CLI

`crill` is a CLI for mobile app UX exploration and competitive change
detection. It prepares a device, scans an app by exploring its UI, records the
run as a replayable artifact, and reuses that artifact for replay and diff.

This repository is the **public binary distribution and operator-facing usage
skill** for `crill`. It intentionally does **not** contain product source
code; the source of truth lives in a private repository. This repo exists so
binary artifacts can be downloaded anonymously by Homebrew and other
installer flows.

<!-- SCREENSHOT: hero (scan progress or final report card). Coming soon. -->

## Why Crill

`crill` is building toward a simple promise:

- **Agents that see like humans**: explore mobile UI the way a product
  reviewer or operator actually encounters it, not as a flat dump of XML.
- **Perspective-guided UX review**: scan the same app from reusable lenses
  such as a novice user, expert user, onboarding reviewer, or
  accessibility-focused evaluator.
- **Exploration + replay + diff in one pipeline**: discover a flow once, keep
  the artifact, replay it later, and compare runs without rebuilding context
  from scratch.

Positioning in one line:

> Perspective-guided mobile UX exploration for PMs, founders, and operators —
> grounded in HCI research on how people actually see and evaluate mobile
> UIs, turning autonomous scans into replayable product evidence and
> competitive diffs.

## What It Does Today

- `setup` prepares iOS automation prerequisites.
- `scan` explores an app through the local automation backend and records a
  replayable scenario.
- `analyze` reads a recorded run and produces a separate LLM-backed analysis
  artifact (UX, replay, acceptance, audit, or diff-risk).
- `replay` re-runs a recorded scenario against the current device.
- `diff` compares two recorded runs and summarizes structural changes.
- `report` renders a localized static HTML view from recorded run artifacts.
- `evidence` renders the deterministic layer of a run without any LLM calls.
- `config baseline` stores a named golden run per app so `diff` can be
  repeated without typing both paths every time.
- `config perspective` stores reusable named evaluation lenses, and
  `scan --perspective` applies them to both exploration and report output.
- `config perspective generate` turns a short natural-language viewpoint into
  a reusable saved lens through the configured LLM provider.
- `provider` manages the LLM provider credentials used for model-backed
  exploration.
- `auth` is the operator-identity gate: gated commands refuse to run until
  the operator has a live session.

<!-- SCREENSHOT: cli-output (terminal showing scan in progress). Coming soon. -->

## Feature Highlights

### Autonomous app exploration

`crill scan` walks the UI, records each step, captures screenshots, and
emits both a final scenario artifact and in-progress machine-readable events.

### Perspective-guided evaluation

Run the same product from different reusable lenses:

- `--perspective novice` for first-run clarity and discoverability
- `--perspective expert` for dense navigation, shortcuts, and power-user flow
- `--perspective "Does this onboarding convey value in 30 seconds?"` for a
  one-off PM question
- `crill config perspective generate onboarding-review "A first-time user
  deciding in 30 seconds whether this product is worth continuing."` for a
  reusable AI-generated lens you can apply again later

When a scan uses a perspective, the report includes a `Perspective
evaluation` section showing the active lens plus blocked and fallback
signals observed under it.

### Replayable product evidence

`crill` does not stop at a terminal transcript. The recorded run becomes a
reusable evidence artifact that `analyze`, `replay`, `diff`, and `report`
all consume directly.

### Separate evidence from interpretation

The scenario artifact is the deterministic run record. The analysis artifact
is an optional run-level LLM interpretation generated afterward. The diff
analysis artifact is the matching diff-level interpretation. `evidence`
renders the deterministic layer, and `report` renders the final presentation
layer. Neither makes hidden model calls.

### Competitive change detection

Diff two recorded runs, generate a structural summary, optionally add an
LLM-written natural-language summary, and share a localized HTML report
instead of raw JSON.

### Isolated, schema-enforced LLM calls

Every model-backed decision runs as a bounded subprocess with uniform
discipline across providers: session-less invocation, declared input and
output schemas, a per-call timeout, separated stdout and stderr, and
post-parse structural validation before the payload reaches the scan
loop. The invariants are declared as tests in the source repository so
that a reader does not have to reconstruct the harness from every
provider method.

<!-- SCREENSHOT: diff-report (HTML report showing a side-by-side diff). Coming soon. -->

## Honest Support Matrix

`crill` is in early access. The current supported surface is intentionally
narrow:

- **Host**: macOS only (Apple Silicon).
- **Target platform**: iOS real device only. Android infrastructure exists
  in the codebase but is not validated at this stage.
- **Reliability**: iOS real-device runs can still fail around Xcode provider
  liveness or WebDriverAgent launch. Recovery paths are documented; most
  blockers have an explicit resume command.
- **LLM access**: you bring your own Anthropic or OpenAI key via
  `crill provider login`.

Linux and Windows native distribution is deferred until after the macOS
surface stabilizes.

## Install

```bash
brew install corca-ai/tap/crill
crill --version
```

The tap currently ships an unsigned binary. The first run is blocked by
macOS Gatekeeper; right-click `/usr/local/bin/crill` (or
`/opt/homebrew/bin/crill` on Apple Silicon) in Finder, choose **Open**, and
confirm once to add it to the Gatekeeper exception list. After that,
`crill` runs from any terminal without friction. Signed and notarized
distribution is coming soon.

A one-line curl installer and a signed macOS app bundle are coming soon.

For a step-by-step install flow aimed at an agent driving a Mac + iPhone pair
(including what `crill setup --ios` automates and the human-only steps it
hands back), see [`docs/install.md`](docs/install.md). For the first internal
iOS trial session script, see
[`docs/internal-ios-trial.md`](docs/internal-ios-trial.md).

<!-- SCREENSHOT: install-flow (first-run Gatekeeper confirmation). Coming soon. -->

## Access Control

Installing the binary is public. Using gated product commands is not.

- `crill auth login <email>` exchanges an invitation for a session token.
- Gated commands (`setup`, `scan`, `replay`, `diff`, `report`, and related)
  fail until the operator has a live session.
- Ungated commands remain available for inspection and recovery:
  `crill --help`, `crill --version`, `crill commands --json`,
  `crill doctor`, `crill uninstall`, `crill runs audit`,
  `crill skills install`, `crill auth ...`, `crill provider ...`.

## Quick Start

Log in to the access gate with the invitation key sent to you, then
configure an LLM provider and prepare a device:

```bash
crill auth login your@email.example
crill provider login anthropic --key "$ANTHROPIC_API_KEY"
crill setup --ios
```

Run a first scan and explore the outputs:

```bash
crill scan com.example.app --platform ios --max-actions 10 --max-states 10
crill scan com.example.app --platform ios --perspective novice
crill evidence runs/<timestamp>/
crill analyze runs/<timestamp>/ --question "What is the biggest UX risk in this run?"
crill report runs/<timestamp>/
crill runs audit runs/<timestamp>/
```

Reuse the recorded artifact:

```bash
crill replay runs/<timestamp>/scenario.yaml
crill diff runs/baseline runs/current
crill config baseline set com.example.app runs/baseline
crill config perspective set onboarding-review "Evaluate clarity, motivation, and friction for a first-time user."
crill config perspective generate senior-user "An older mobile user who needs clear labels, large tap targets, and strong trust signals during payment."
```

On the first interactive run, `crill` asks for the CLI/report language and
saves it. Config and artifact keys stay in English; CLI guidance and
generated reports use the selected language.

## Running Doctor

`crill doctor` is a read-only report of your install channel, `~/.crill/`
state, gate reachability, LLM providers, and platform prerequisites. Use it
any time a run is misbehaving:

```bash
crill doctor
crill doctor --json   # agent-consumable output
```

`crill runs audit` is the quickest binary-level telemetry summary for a saved
run. It reports artifact depth plus latency, token, and cost metrics from the
persisted scenario packet. Add `--baseline <run>` to compare a new run against
the previous good one, and optional regression budgets when QA or automation
should fail fast on slower or more expensive exploration:

```bash
crill runs trend com.example.app
crill runs budget set qa-default --max-llm-avg-regression-ms 1000 --max-total-token-regression 500 --max-breadth-drop 1
crill runs budget fallback qa-default
crill runs budget assign com.example.app qa-default
crill runs trend com.example.app --budget qa-default
crill runs trend com.example.app --max-breadth-drop 1
crill runs audit runs/<timestamp>/
crill runs audit runs/<timestamp>/ --json   # agent-consumable summary
crill runs audit runs/current/ --app com.example.app --budget qa-default
crill runs audit runs/current/ --baseline runs/baseline/ --budget qa-default
crill runs audit runs/current/ --baseline runs/baseline/ --max-llm-avg-regression-ms 1000 --max-total-token-regression 500
```

## Where To Look Next

- `crill --help`, `crill <command> --help`
- `crill commands --json`  *(stable machine-readable command discovery for agents/tools)*
- `crill runs audit --help`  *(artifact depth + latency/token/cost summary)*
- `crill runs trend --help`  *(recent app-level telemetry history and drift view)*
- Agent-driven install guide: [`docs/install.md`](docs/install.md)
- Internal iOS trial script: [`docs/internal-ios-trial.md`](docs/internal-ios-trial.md)
- Public operator skill: [`skills/crill`](skills/crill)
- Shared first-run contract: [`skills/crill/references/onboarding.md`](skills/crill/references/onboarding.md)
- iOS real-device reference: [`skills/crill/references/ios-real-device.md`](skills/crill/references/ios-real-device.md)
- Public release notes: [releases](https://github.com/corca-ai/crill-cli/releases)

## Latest Public Release

- Version: `0.5.4`
- Release: https://github.com/corca-ai/crill-cli/releases/tag/v0.5.4
- Mirrored from upstream release: https://github.com/corca-ai/crill/releases/tag/v0.5.4
