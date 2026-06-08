# @tracertm/desktop-electrobun

TraceRTM desktop shell built on [Electrobun](https://github.com/blackboardsh/electrobun): Bun runtime plus the host system webview, using WKWebView on macOS, WebView2 on Windows, and WebKitGTK on Linux.

This guide covers end-user expectations, developer setup, local service boot, packaging, and common troubleshooting.

## Prerequisites

- Bun 1.1.x. The frontend workspace is pinned to Bun 1.1.38.
- One supported desktop OS:
  - macOS 12 or newer
  - Windows 10 or newer
  - Ubuntu 22.04 or newer
- About 500 MB of free disk space for dependencies, build artifacts, and distributables.
- `process-compose` available in `PATH` for one-click service boot.
- Platform webview runtime:
  - macOS: WKWebView is provided by the OS.
  - Windows: Microsoft Edge WebView2 Runtime must be installed.
  - Linux: WebKitGTK packages must be available from the OS distribution.

## Install dependencies

From the app directory, install Bun dependencies:

`cd frontend/apps/desktop-electrobun && bun install`

Run this after cloning the repo and whenever lockfile or package metadata changes.

## Development mode

Development mode starts the desktop shell and points it at the web renderer.

1. Ensure the web app is running on `http://localhost:3000`.
2. From `frontend/apps/desktop-electrobun`, run `bun run dev`.

The desktop app expects the renderer at port `3000` in dev mode. Override it with `TRACERTM_RENDERER_URL` if the web app is served elsewhere.

## Build distributables

Build platform-specific distributables from `frontend/apps/desktop-electrobun`:

- macOS: `bun run package:mac`
- Windows: `bun run package:win`
- Linux: `bun run package:linux`

Packaging is per-OS. Build the macOS package on macOS, the Windows package on Windows, and the Linux package on Linux unless the Electrobun toolchain for a target explicitly supports cross-packaging in your environment.

## Output locations

Packaged outputs are written under `dist/` in this app directory. Depending on the target platform, expect artifacts such as:

- `dist/TraceRTM.app` for macOS
- `dist/TraceRTM.exe` or a Windows installer/executable bundle for Windows
- `dist/TraceRTM` or a Linux package/bundle for Linux

The exact artifact names can vary with Electrobun configuration and platform packaging settings, but `dist/` is the distribution directory to inspect after a successful package run.

## One-click service boot

The desktop entrypoint, `src/main.ts`, shells out to `process-compose up -d` and points it at the repository-root `process-compose.yml`. This lets the desktop app bring up its local service stack before opening the window.

Services started by that compose file include:

- Postgres
- Redis
- NATS
- Go backend
- Web dev server

In development, the BrowserWindow loads the web dev server, normally `http://localhost:3000`. In packaged production builds, the app can load the bundled renderer assets.

## Environment variables

- `TRACERTM_RENDERER_URL`: renderer URL loaded by the desktop shell, commonly `http://localhost:3000` for development.
- `TRACERTM_GATEWAY_URL`: backend or gateway URL used by the desktop shell and renderer when they need to reach the TraceRTM API.
- `DB_PASSWORD`: Postgres password used by the local service stack.

Set these in your shell or process manager before launching the desktop app when you need to override defaults.

## Architecture

```
[BrowserWindow (WKWebView/WebView2/WebKitGTK)] <-> [Bun main process] <-> [process-compose] <-> [Go backend / Postgres / Redis / NATS]
```

Project layout:

```
desktop-electrobun/
  electrobun.config.ts   # app identity, build entrypoints, runtime config
  src/
    main.ts              # Bun main process: service boot + window + menu
  dist/                  # packaged desktop outputs
```

## Troubleshooting

### Port 3000 is already in use

The dev renderer expects the web app on `http://localhost:3000`. If another process owns that port, stop the conflicting process or run the web app on another port and set `TRACERTM_RENDERER_URL` to the new URL before running `bun run dev`.

### `process-compose` is not in `PATH`

One-click service boot requires `process-compose`. Install it for your platform, then confirm `process-compose` resolves in the same terminal that launches the desktop app. If it is installed but not found, update `PATH` or launch the app from an environment that includes the binary.

### WebView2 is missing on Windows

Windows builds require Microsoft Edge WebView2 Runtime. If the app opens to a blank window, fails to create a webview, or reports WebView2 initialization errors, install the current WebView2 Runtime from Microsoft and relaunch the app.

### Renderer does not load

Confirm the web dev server is reachable at `TRACERTM_RENDERER_URL`, usually `http://localhost:3000`. Also confirm the local Go backend and supporting services are running if the renderer loads but API calls fail.

## License

MIT, same as the repository root license.
