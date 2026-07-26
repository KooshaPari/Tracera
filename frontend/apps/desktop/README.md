# Tracera Desktop

A native desktop wrapper for the Tracera local runtime.
web UI. Ships as a real installable app via **Electrobun** — the Phenotype org
standard desktop shell (replaces the former Electron wrapper).

## What this is

The desktop app connects to the durable local Tracera server at
`http://127.0.0.1:8080/` by default. A hosted URL is never selected implicitly.
The React SPA is wrapped in a native WKWebView window
with a system tray icon — giving you a real desktop application experience.

The desktop shell loads the local runtime by default. Hosted/staging URLs are
explicit opt-ins through the environment variables below.

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
| `TRACERA_URL` | Explicit target URL override (including staging/hosted deployments). |
| `TRACERA_HOSTED_URL` | Explicit hosted deployment override (lower precedence than `TRACERA_URL`). |
| `TRACERA_DEV_URL` | Dev URL override (e.g. `http://localhost:5173`). |

URL precedence: `TRACERA_URL` > `TRACERA_HOSTED_URL` > `TRACERA_DEV_URL` > local default.

The resolved target URL is shown in the tray menu under "Target: …".

To have the `.app` start and stop the desktop-hosted stack, opt in explicitly:

```bash
TRACERA_LOCAL_COMPOSE=1 TRACERA_REPO_ROOT=/absolute/path/to/Tracera bun run dev
```

For an explicit bundled Compose stack, set `TRACERA_URL=http://127.0.0.1:18081/`.
The launcher then waits for `/health` and `/ready`, and runs `docker compose down`
when the app exits. The packaged default does not require a bundled CLI.
It rejects port 8080 because that port belongs to Grapheon. The default app
mode remains external-URL-only and does not mutate host services.

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

## Migration from Electron

This shell replaced the retired Electron/electron-builder packaging path. The
`electron/main.js` and `electron/preload.js` files have been removed. The
equivalent Electrobun files are:

| Old (Electron) | New (Electrobun) |
|----------------|-----------------|
| `electron/main.js` | `src/index.ts` |
| `electron/preload.js` | RPC schema in `src/rpc.ts` |
| `package.json` `"build"` section | `electrobun.config.ts` |
| `npm install` / legacy Electron packaging | `bun install` / `bunx electrobun build` |
