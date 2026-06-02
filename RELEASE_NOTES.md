# Sound Control v0.1.0

First public MVP release.

## Highlights

- Menu bar app for process-level macOS volume control.
- Per-app volume slider and mute state.
- CoreAudio Process Tap audio path with private aggregate devices.
- JSON-backed settings persisted by bundle identifier.
- Local verification utility: `SoundControlChecks`.

## Installation

1. Download `SoundControl-v0.1.0-macOS.zip`.
2. Unzip it and move `SoundControl.app` to `/Applications`.
3. Launch the app.
4. Grant macOS Screen & System Audio Recording permission if prompted.
5. Restart the app after granting permission.

Because this build is ad-hoc signed and not notarized, macOS may require opening it from Finder with **Control-click -> Open** the first time.

## Known Limits

- Process-level only; browser tabs and windows are not separated.
- No boost above 100%.
- No global hotkeys yet.
- Output-device changes while apps are tapped may require restarting the app.
- This is a self-use MVP, not a notarized production installer.
