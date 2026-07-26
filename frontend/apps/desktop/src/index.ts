/**
 * Tracera desktop — Electrobun main process (bun side).
 *
 * Responsibilities:
 *  1. Open a BrowserWindow loading the Tracera web UI URL.
 *  2. Set up a system tray icon with a context menu (Show, Reload, Quit).
 *  3. Expose a minimal RPC surface for the webview (target URL, version, reload).
 *  4. On launch, start the bundled Tracera stack via `bin/tracera` so the
 *     desktop app is fully self-contained — no external gh-pages or hosted
 *     backend required.
 *
 * Target URL precedence (first wins):
 *   1. TRACERA_URL env var  (explicit override; e.g. staging)
 *   2. TRACERA_DEV_URL env var (legacy dev override)
 *   3. Default: bundled local URL (http://127.0.0.1:18081)
 *
 * The bundled CLI (bin/tracera) auto-detects the host's container runtime
 * (apple-container > docker > podman > wsl+docker), starts Compose, and
 * waits for /health. Pass TRACERA_SKIP_BUNDLE=1 to disable auto-start
 * (useful when targeting the bundled URL but managing the stack externally).
 */

import { BrowserWindow, Tray, defineElectrobunRPC, type MenuItemConfig } from "electrobun/bun";
import type { BunRequests, WebviewRequests } from "./rpc";
import { LOCAL_URL, resolveBundleCli, startBundle } from "./compose";
import { resolveTargetUrl } from "./target";

const APP_VERSION = "0.1.0";
const skipBundle = process.env.TRACERA_SKIP_BUNDLE === "1";

const targetUrl = resolveTargetUrl(process.env);

function log(...args: unknown[]): void {
  console.log("[tracera-desktop]", ...args);
}

let stopBundle: (() => Promise<void>) | undefined;
if (!skipBundle && targetUrl.startsWith(LOCAL_URL)) {
  // We're targeting the bundled local URL — ensure the stack is running.
  const cliPath = resolveBundleCli(import.meta.dir);
  if (!cliPath) {
    log("bundled tracera CLI not found; skipping auto-start. Run `cargo build --release -p tracera-cli` and rebuild the .app to enable.");
  } else {
    log("starting bundled stack via", cliPath);
    try {
      stopBundle = await startBundle({ cliPath, log, localUrl: targetUrl });
      log("bundled stack healthy at", targetUrl);
    } catch (err) {
      log("bundled stack startup failed:", err instanceof Error ? err.message : err);
    }
  }
}

log("target URL:", targetUrl);

// ---------------------------------------------------------------------------
// RPC (bun side)
// ---------------------------------------------------------------------------

const rpc = defineElectrobunRPC<{ bun: BunRequests; webview: WebviewRequests }>(
  "bun",
  {
    handlers: {
      requests: {
        getTargetUrl: () => targetUrl,
        getVersion: () => APP_VERSION,
        reload: () => {
          win.webview.loadURL(targetUrl);
        },
      },
    },
  },
);

// ---------------------------------------------------------------------------
// Main window
// ---------------------------------------------------------------------------

const win = new BrowserWindow({
  title: "Tracera",
  frame: { x: 100, y: 100, width: 1280, height: 820 },
  url: targetUrl,
  titleBarStyle: "hiddenInset",
  rpc,
});

log("window created, id=", win.id);

// ---------------------------------------------------------------------------
// System tray
// ---------------------------------------------------------------------------

function buildTrayMenu(): Array<MenuItemConfig> {
  return [
    { type: "normal", label: "Show Tracera", action: "show-window" },
    { type: "separator" },
    { type: "normal", label: "Reload", action: "reload-window" },
    { type: "separator" },
    { type: "normal", label: `Target: ${targetUrl}`, enabled: false },
    { type: "separator" },
    { type: "normal", label: "Quit Tracera", action: "quit" },
  ];
}

const tray = new Tray({ title: "Tracera" });
tray.setMenu(buildTrayMenu());

tray.on("tray-clicked", (event: unknown) => {
  const e = event as { action?: string } | null;
  const action = e?.action ?? "";

  if (action === "show-window" || action === "") {
    win.show();
  } else if (action === "reload-window") {
    win.webview.loadURL(targetUrl);
  } else if (action === "quit") {
    log("quit via tray");
    process.exit(0);
  }
});

log("tray created, id=", tray.id);

// Keep the process alive even when the window is closed (tray-resident app).
process.on("beforeExit", () => {
  tray.remove();
  void stopBundle?.();
});
