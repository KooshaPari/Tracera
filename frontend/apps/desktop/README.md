# Tracera Desktop

A native desktop wrapper for the [Tracera](https://kooshapari.github.io/Tracera/)
web UI. Ships as a real installable app for macOS, Windows, and Linux.

## What this is

The web app at `https://kooshapari.github.io/Tracera/` is a Vite-built
React SPA. This Electron app wraps that SPA in a native window so you
can have Tracera as a real desktop application — dock icon, system
tray, installable, persistent between reboots.

The desktop shell is **dumb on purpose**: it loads whatever URL you
point it at. By default it points at the production Pages deployment,
but you can override it (see Configuration below).

## Install (dev)

```bash
cd frontend/apps/desktop
npm install
npm start                # loads the production Tracera
npm run start:dev        # loads http://localhost:5173 (run web dev server first)
```

## Build (release)

Cross-platform installers are produced by `electron-builder`.

```bash
npm install
npm run build:mac        # .dmg + .zip for arm64 + x64
npm run build:win        # .exe NSIS installer + portable
npm run build:linux      # AppImage + .deb
npm run build            # current platform
```

Build artifacts land in `frontend/apps/desktop/release/<version>/`.

## Configuration

| Env var              | Purpose                                              |
| -------------------- | ---------------------------------------------------- |
| `TRACERA_URL`        | Override the target URL (default: Pages production). |
| `TRACERA_DEV_URL`    | Dev URL (only used when `--dev` flag or `TRACERA_DEV_URL` set). |
| `npm run start:dev`  | Sets `TRACERA_DEV_URL=http://localhost:5173`.        |

The resolved target URL is shown in the tray menu under "Target: …".

## Features

- **Single-instance lock** — re-launching the app focuses the existing window.
- **System tray** — right-click for Show / Reload / Open DevTools / Quit.
- **Close-to-tray** — closing the window keeps the app alive in the tray.
- **External links** — open in the user's default browser, not in-app.
- **Persistent bounds** — window size/position remembered between sessions.
- **Sandboxed renderer** — context isolation on, no Node in renderer, preload bridge only.

## Architecture

```
+-------------------------+         +----------------------+
|  Renderer (Tracera UI)  |  <--->  |  Preload (contextBridge)  |
+-------------------------+         +----------------------+
                                                   |
                                                   v
                                         +----------------------+
                                         |  Main process        |
                                         |  - BrowserWindow     |
                                         |  - Tray + Menu       |
                                         |  - IPC handlers      |
                                         +----------------------+
```

The renderer has **no Node.js access**. It can only call the explicit
methods exposed by `preload.js` (`window.tracera.getTargetUrl()`,
`window.tracera.getVersion()`).

## Releasing

The `.github/workflows/release-desktop.yml` workflow builds installers
on tag pushes matching `v*` (e.g. `git tag v0.1.3 && git push --tags`).
It produces:

- macOS: `.dmg` (arm64, x64) + `.zip` (arm64, x64)
- Windows: NSIS `.exe` + portable `.exe`
- Linux: AppImage + `.deb`

…and attaches them as GitHub Release assets.

## Icons

electron-builder needs PNG/ICO/ICNS files at standard paths:

- `build/icon.png` — Linux
- `build/icon.ico` — Windows
- `build/icon.icns` — macOS

If these files are missing, electron-builder falls back to a default Electron icon.
To customize, drop your brand icons in `frontend/apps/desktop/build/`
(*note: the `build/` subdir is locally gitignored in some environments; the directory
itself is created on first electron-builder invocation*) and re-run `npm run build`.