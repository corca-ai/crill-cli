# iOS Real-Device Failure Map

Use this map only after reading the current `crill` output and the current
agent-device or Xcode error text.

This file is a diagnosis aid, not a checklist. Match the exact current failure
before giving advice. If the binary already printed a narrower blocker, trust
the binary over this file.

## Resume Command

Do not trust this file for current scan flags or defaults. Inspect the current
binary help or output and compose the resume command from the user's actual
target plus the current CLI surface.

## Failure Map

### `The developer disk image could not be mounted on this device`

- Meaning: DDI is not mounted yet.
- Common causes:
  - iPhone is locked
  - selected Xcode does not support the device OS
- Human step:
  - keep the phone awake and unlocked
  - if the selected Xcode is too old, install or select a supported full Xcode

### `iPhone Developer Mode is off.` / readiness check `ios.developer_mode`

- Meaning: iOS 16+ requires Developer Mode on the iPhone before any free-team
  build can launch.
- Where it surfaces:
  - the `crill doctor --ios-readiness` aggregator prints a four-part blocker
  - the first real-device scan refuses to proceed with the same blocker
- Human step:
  - on the iPhone, open `Settings -> Privacy & Security -> Developer Mode`
  - toggle it on, then confirm the device restart prompt
  - re-run the resume command printed by the binary

### `No provider was found.`

- Meaning: Xcode's device-provider backend is unavailable even if the Xcode UI
  still shows an account, team, or provisioned device.
- Precedence: when the same `xcodebuild` failure also contains `No Accounts:
  Add a new account`, `No profiles for ... were found`, or `couldn't find any
  iOS App Development provisioning profiles`, the binary now classifies the
  failure as a signing-hint case (next entry) instead of a provider case.
  Trust that classification and do not pre-emptively restart
  `CoreDeviceService`.
- Binary action:
  - try host-side recovery first, such as launching Xcode if needed and
    restarting `CoreDeviceService`
- Human step:
  - only if host-side recovery failed, open `Xcode -> Settings -> Accounts`
  - confirm the Apple account and team are still present
  - sign out and sign back in only as the last escalation, not the first

### `No profiles for '...' were found` / `No Accounts: Add a new account`

- Meaning: signing is the real blocker, even though `xcodebuild` may also
  print `No provider was found.` as a downstream diagnostic crumb.
- Human step:
  - open `Xcode -> Settings -> Accounts` and confirm at least one Apple ID
    is present; add one if none is configured
  - open the project's `Signing & Capabilities` tab and let Xcode generate
    or download the missing `Apple Development` certificate / provisioning
    profile
  - re-run the resume command printed by the binary
- Do not jump to `CoreDeviceService` restart for this branch — the
  provider-missing recovery does not fix a missing account or profile.

### `xcodebuild failed with code 70`

- Meaning: signing is not ready.
- Human step:
  - open `Xcode -> Settings -> Accounts`
  - confirm the team is visible
  - open `Manage Certificates...` and create or download `Apple Development`

### `Developer App Certificate is not trusted`

- Meaning: the iPhone has not trusted the developer app certificate yet.
- Binary action:
  - on a trust failure, keep the runner app visible long enough for the
    developer cert to appear in `Settings -> General -> VPN & Device
    Management`.
- Human step:
  - open `Settings -> General -> VPN & Device Management` on the iPhone
  - trust the developer app certificate for the Apple ID or team
  - re-run the resume command printed by the binary

### `Timed out while enabling automation mode`

- Meaning: signing or trust may already be solved, but the agent-device iOS
  runner still failed to enter UI automation mode.
- Operator guidance:
  - do not repeat stale signing steps unless the current logs reintroduce them
  - capture the exact agent-device or Xcode log
  - check whether the device shows a fresh trust, permission, or system alert
  - keep the device unlocked during repro
