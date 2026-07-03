/**
 * Tracera desktop — Electrobun main process (bun side).
 *
 * Responsibilities:
 *  1. Open a BrowserWindow loading the Tracera web UI URL.
 *  2. Set up a system tray icon with a context menu (Show, Reload, Quit).
 *  3. Expose a minimal RPC surface for the webview (target URL, version, reload).
 *
 * Target URL precedence (first wins):
 *   1. TRACERA_URL env var
 *   2. TRACERA_DEV_URL env var
 *   3. Default: https://kooshapari.github.io/Tracera/
 *
 * The shell is dumb by design: it does NOT bundle or serve the web UI.
 * It relies on the external deployment. Use TRACERA_URL to override.
 */

import { BrowserWindow, Tray, defineElectrobunRPC, type MenuItemConfig } from "electrobun/bun";
import type { BunRequests, WebviewRequests } from "./rpc";

// ---------------------------------------------------------------------------
// Target URL resolution
// ---------------------------------------------------------------------------

const DEFAULT_URL = "https://kooshapari.github.io/Tracera/";
const APP_VERSION = "0.1.0";

function resolveTargetUrl(): string {
  if (process.env.TRACERA_URL) return process.env.TRACERA_URL;
  if (process.env.TRACERA_DEV_URL) return process.env.TRACERA_DEV_URL;
  return DEFAULT_URL;
}

const targetUrl = resolveTargetUrl();

function log(...args: unknown[]): void {
  console.log("[tracera-desktop]", ...args);
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
    {
      type: "normal",
      label: "Show Tracera",
      action: "show-window",
    },
    { type: "separator" },
    {
      type: "normal",
      label: "Reload",
      action: "reload-window",
    },
    { type: "separator" },
    {
      type: "normal",
      label: `Target: ${targetUrl}`,
      enabled: false,
    },
    { type: "separator" },
    {
      type: "normal",
      label: "Quit Tracera",
      action: "quit",
    },
  ];
}

// Electrobun Tray — constructor handles non-macOS gracefully (logs a warning
// and sets visible=false; the rest of the app continues normally).
const tray = new Tray({ title: "Tracera" });
tray.setMenu(buildTrayMenu());

tray.on("tray-clicked", (event: unknown) => {
  const e = event as { action?: string } | null;
  const action = e?.action ?? "";

  if (action === "show-window" || action === "") {
    // bare click or explicit show
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
});
