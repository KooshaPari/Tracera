# Tracera Desktop

A native desktop wrapper for the [Tracera](https://kooshapari.github.io/Tracera/)
web UI. Ships as a real installable app via **Electrobun** — the Phenotype org
standard desktop shell.

## What this is

The web app at `https://kooshapari.github.io/Tracera/` is a Vite-built
React SPA. This Electrobun app wraps that SPA in a native WKWebView window
with a system tray icon — giving you a real desktop application experience.

The desktop shell loads the canonical local rich-dashboard gateway at
`http://127.0.0.1:18000/` by default. Hosted/staging URLs are explicit opt-ins.

## Stack

| Layer | Technology |
|-------|-----------|
| Shell runtime | [Electrobun](https://electrobun.dev) ^1.18.1 |
| Package manager | bun |
| Main process | TypeScript (`src/index.ts`) |
| No bundled webview | External URL loaded by WKWebView |

## Dev

```bash
cd frontend/apps/desktop
bun install
bun run dev              # opens app loading the configured target URL
```

## Build (release)

```bash
bun install
bun run build            # bunx electrobun build → builds app bundle
bun run package          # bunx electrobun package → cross-platform installer
```

Build artifacts land in `frontend/apps/desktop/build/`.

## Test

```bash
# CI-safe (no display required)
CI=1 bun test tests/e2e_desktop.test.ts

# Host mode (macOS with display — launches the app)
bun test tests/e2e_desktop.test.ts
```

## Configuration

| Env var | Purpose |
|---------|---------|
| `TRACERA_GATEWAY_URL` | Explicit gateway origin (canonical rich-dashboard mode). |
| `TRACERA_URL` | Explicit target URL override (including hosted deployments). |
| `TRACERA_DEV_URL` | Dev URL override (e.g. `http://localhost:5173`). |

URL precedence: `TRACERA_GATEWAY_URL` > `TRACERA_URL` > `TRACERA_HOSTED_URL` > `TRACERA_DEV_URL` > local default.

The resolved target URL is shown in the tray menu under "Target: …".

## Features

- **System tray** — click to Show / Reload / Quit; always present.
- **Minimal RPC** — webview can call `getTargetUrl()`, `getVersion()`, `reload()`.
- **Tray-resident** — the app stays alive in the tray when the window is closed.
- **External URL mode** — no bundled web assets; loads the deployed Tracera SPA.

## Architecture

```
+------------------------------+      Electrobun RPC      +------------------------------+
|   WKWebView                  |  <------------------->   |   Bun main process           |
|   (Tracera web UI — SPA)     |                          |   src/index.ts               |
|   External URL or dev server |                          |   - BrowserWindow (WKWebView) |
+------------------------------+                          |   - Tray + context menu       |
                                                          |   - RPC: getTargetUrl,        |
                                                          |     getVersion, reload        |
                                                          +------------------------------+
```

## Icons

Place macOS iconset in `assets/icons/Tracera.iconset/` (standard sizes 16–1024).
Electrobun's build step runs `iconutil` to produce `AppIcon.icns`. If absent,
Electrobun uses its default icon.
