# iOS Real-Device Failure Map

Use this map only after reading the current `crill` output and the current
Appium or Xcode error text.

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

### `No provider was found.`

- Meaning: Xcode's device-provider backend is unavailable even if the Xcode UI
  still shows an account, team, or provisioned device.
- Binary action:
  - try host-side recovery first, such as launching Xcode if needed and
    restarting `CoreDeviceService`
- Human step:
  - only if host-side recovery failed, open `Xcode -> Settings -> Accounts`
  - confirm the Apple account and team are still present
  - sign out and sign back in only as the last escalation, not the first

### `xcodebuild failed with code 70`

- Meaning: signing is not ready.
- Human step:
  - open `Xcode -> Settings -> Accounts`
  - confirm the team is visible
  - open `Manage Certificates...` and create or download `Apple Development`

### `Developer App Certificate is not trusted`

- Meaning: the iPhone has not trusted the developer app certificate yet.
- Human step:
  - open `Settings -> General -> VPN & Device Management` on the iPhone
  - trust the developer app certificate for the Apple ID or team

### `Timed out while enabling automation mode`

- Meaning: signing or trust may already be solved, but WDA still failed to enter
  UI automation mode.
- Operator guidance:
  - do not repeat stale signing steps unless the current logs reintroduce them
  - capture the exact Appium or Xcode log
  - check whether the device shows a fresh trust, permission, or system alert
  - keep the device unlocked during repro
