## App identity

TraceRTM v0.1.0 — `com.tracertm.desktop`

## Downloads

| Platform  | Artifact                                  | Size |
|-----------|-------------------------------------------|------|
| macOS     | `TraceRTM-0.1.0-mac.dmg`                  | -    |
| Windows   | `TraceRTM-0.1.0-win.exe`                  | -    |
| Linux     | `TraceRTM-0.1.0-linux.AppImage`           | -    |
| Linux     | `TraceRTM-0.1.0-linux.deb`                | -    |
| Linux     | `TraceRTM-0.1.0-linux.rpm`                | -    |

## Install instructions

- **macOS** — Open the DMG, drag `TraceRTM.app` to `/Applications`. First launch: right-click → Open to bypass Gatekeeper.
- **Windows** — Run the EXE installer. SmartScreen: choose "More info" → "Run anyway".
- **Linux AppImage** — `chmod +x TraceRTM-0.1.0-linux.AppImage && ./TraceRTM-0.1.0-linux.AppImage`
- **Linux .deb** — `sudo dpkg -i TraceRTM-0.1.0-linux.deb && sudo apt-get install -f`
- **Linux .rpm** — `sudo rpm -Uvh TraceRTM-0.1.0-linux.rpm`

## What's new

_Auto-generated from conventional commits._

### Features
<!-- feat: commits -->

### Bug fixes
<!-- fix: commits -->

### Documentation
<!-- docs: chore: commits -->

### Infrastructure
<!-- ci: commits -->

## Known issues

- _None reported._

<!-- Add issues below, e.g.: -->
<!-- - Crash on resume from sleep — GH#42 -->

## SHA256 checksums

```
<checksums-placeholder>
```

<!-- Format:  <sha256>  TraceRTM-0.1.0-<artifact> -->

## Code signing status

| Platform | Status |
|----------|--------|
| macOS    | Signed by Apple Developer ID (`com.tracertm.desktop`) |
| Windows  | Signed via Windows EV certificate |
| Linux    | Signed with maintainer GPG key (`<key-id>`) |

<!-- Verification commands: -->
<!-- macOS:   codesign -dv --verbose=4 /Applications/TraceRTM.app -->
<!-- Windows: Get-AuthenticodeSignature TraceRTM-0.1.0-win.exe -->
<!-- Linux:   gpg --verify TraceRTM-0.1.0-linux.AppImage.asc -->
