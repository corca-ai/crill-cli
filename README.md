# Crill CLI

`crill` is a CLI for mobile app UX exploration and competitive change
detection. It prepares a device, scans an app by exploring its UI, records the
run as a replayable artifact, and reuses that artifact for replay and diff.

This repository is the **public binary distribution and operator-facing usage
skill** for `crill`. It intentionally does **not** contain product source
code; the source of truth lives in a private repository. This repo exists so
binary artifacts can be downloaded anonymously by the direct `install.sh`
installer flow.

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

- `doctor --ios-readiness` surfaces real-device readiness blockers before a scan.
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
- **Target platform**: iOS internal-QA on real device or simulator. Real
  device remains the primary path; simulator is the supported Tier 2 path.
- **Reliability**: real-device runs can still fail around Xcode provider
  liveness, signing, device trust, or agent-device runner launch. Simulator runs are supported for
  prepared-device and phone-free checks. Recovery paths are documented; most
  blockers have an explicit resume command.
- **LLM access**: you bring your own Anthropic or OpenAI key via
  `crill provider login`.

Linux and Windows native distribution is deferred until after the macOS
surface stabilizes.

## Install

Current prebuilt support is Apple Silicon macOS only.

```bash
curl -sSfL https://raw.githubusercontent.com/corca-ai/crill-cli/main/install.sh | sh
crill --version
```

`install.sh` is the primary internal-QA path. It installs the binary into
`~/.local/bin`, provisions the owned iOS runtime under `~/.crill/`, repairs
PATH reachability when needed, and keeps the install surface inside `crill`'s
own control instead of depending on an external package manager.
The same install step now materializes `~/.crill/runtime.json` and
`~/.crill/runtime/current/` for the owned Node/agent-device runtime.

The installer currently ships an unsigned binary. If macOS blocks the first
launch, right-click the bundled binary in Finder, choose **Open**, and confirm
once to add it to the Gatekeeper exception list. Signed and notarized
distribution is coming later.

For a step-by-step install flow aimed at an agent driving a Mac with either a
connected iPhone or an iOS simulator (including iOS readiness checks and the
human-only steps they hand back), see
[`docs/install.md`](docs/install.md).

<!-- SCREENSHOT: install-flow (first-run Gatekeeper confirmation). Coming soon. -->

## Access Control

Installing the binary is public. Using gated product commands is not.

- `crill auth login <email>` creates a session token; trusted internal
  domains can sign in without an invitation key.
- Gated commands (`scan`, `replay`, `diff`, `report`, and related)
  fail until the operator has a live session.
- Ungated commands remain available for inspection and recovery:
  `crill --help`, `crill --version`, `crill commands --json`,
  `crill doctor`, `crill uninstall`, `crill runs audit`,
  `crill skills install`, `crill auth ...`, `crill provider ...`.

## Quick Start

Supported first-run path prerequisites:

- one Mac
- either one iPhone plus USB cable, or Xcode with an available iOS simulator
- the target app available on the chosen iPhone or simulator
- for real-device work, Apple ID already signed into Xcode or macOS System Settings

Install the binary, sign in, and install the public skill:

```bash
curl -sSfL https://raw.githubusercontent.com/corca-ai/crill-cli/main/install.sh | sh
crill --version
crill auth login <email>
crill skills install
crill doctor --next-action
```

If you want an agent to drive the rest, give it this prompt:

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

You can still run the steps manually. After signing in, configure an LLM
provider and check iOS readiness before the first scan:

```bash
crill auth login your@email.example
crill provider login anthropic --key "$ANTHROPIC_API_KEY"
crill doctor --ios-readiness
crill ios apps --json
```

Run a first quick-check scan and explore the outputs:

```bash
crill scan com.example.app --platform ios --max-actions 10 --max-states 10
crill scan com.example.app --platform ios --perspective novice
crill evidence runs/<timestamp>/
crill analyze runs/<timestamp>/ --question "What is the biggest UX risk in this run?"
crill report runs/<timestamp>/
crill runs audit runs/<timestamp>/
```

Participant-facing scan-depth names:

- `quick check`: `--max-actions 10 --max-states 10`
- `standard exploration`: omit both flags and use the default scan limits
- `deeper exploration`: increase both flags intentionally after the first run succeeds

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
crill doctor --next-action   # one machine-friendly next onboarding step
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
- Public operator skill: [`skills/crill`](skills/crill)
- Shared first-run contract: [`skills/crill/references/onboarding.md`](skills/crill/references/onboarding.md)
- iOS real-device reference: [`skills/crill/references/ios-real-device.md`](skills/crill/references/ios-real-device.md)
- Public release notes: [releases](https://github.com/corca-ai/crill-cli/releases)

## Latest Public Release

- Version: `0.5.10`
- Release: https://github.com/corca-ai/crill-cli/releases/tag/v0.5.10
- Mirrored from upstream release: https://github.com/corca-ai/crill/releases/tag/v0.5.10
