# @tracertm/desktop-electrobun

Tracera desktop shell built on [Electrobun](https://github.com/blackboardsh/electrobun) — Bun runtime + system webview (WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux).

## Architecture

```
desktop-electrobun/
  electrobun.config.ts   # app identity, build entrypoints, runtime config
  src/
    main.ts              # Bun main process: service boot + window + menu
```

**Service boot (one-click):** On launch, `main.ts` runs `process-compose up -d` pointing at the repo root `process-compose.yml`. This brings up Postgres, Redis, NATS, the Go backend, and the web dev server automatically before the window opens.

**Renderer:** In dev mode set `TRACERTM_RENDERER_URL=http://localhost:3000`. In production the bundled `views://web/index.html` (built `@tracertm/web` dist) is used.

## Dev (requires macOS for Electrobun builds)

```bash
# From repo root — start all services AND web dev server
process-compose up

# In another terminal, launch the Electrobun shell
cd frontend/apps/desktop-electrobun
bun install
bun dev
# Or point at already-running web:
TRACERTM_RENDERER_URL=http://localhost:3000 bun dev
```

## Production build (macOS only — Electrobun CLI requires macOS)

```bash
cd frontend/apps/desktop-electrobun
bun install
bun build:release
# Output: dist/ — self-extracting bundle for distribution
```

## Windows notes

Electrobun **runs** on Windows 11+ (WebView2/Edge), but the **build toolchain** (`electrobun build`) requires macOS. CI should build on a macOS runner; the output `.exe` distributable runs on Windows.

## Replacing Electron

The old Electron shell at `../desktop` is kept intact. Once the Electrobun shell is validated:
1. Delete `../desktop` or archive it.
2. Update workspace `package.json` to point at `desktop-electrobun`.
3. Update any CI that references `@tracertm/desktop`.
