#!/usr/bin/env bun
/**
 * Tracera desktop main process.
 *
 * The shell owns the window/tray lifecycle and delegates service orchestration
 * to the bundled `tracera` CLI.  The rich dashboard gateway remains the
 * default target; callers may override it explicitly for staging or a local
 * packaged stack.
 */

import { BrowserWindow, Tray, defineElectrobunRPC, type MenuItemConfig } from "electrobun/bun";
import type { BunRequests, WebviewRequests } from "./rpc";
import { resolveBundleCli, startBundle, LOCAL_URL } from "./bundle.js";
import { resolveTargetUrl } from "./target.js";

const APP_VERSION = "0.1.0";
const log = (...args: unknown[]) => console.log("[tracera-desktop]", ...args);
const targetUrl = resolveTargetUrl(process.env);
const skipBundle = process.env.TRACERA_SKIP_BUNDLE === "1";
let stopBundle: (() => Promise<void>) | undefined;

log("target URL:", targetUrl);

// The packaged legacy stack is opt-in.  Rich mode (18000) is supplied by the
// gateway supervisor/Compose wrapper and must never be silently replaced by
// the old 18081 frontend-only stack.
if (!skipBundle && targetUrl.startsWith(LOCAL_URL) && resolveBundleCli(import.meta.dir)) {
  try {
    log("starting bundled stack...");
    stopBundle = await startBundle({ localUrl: targetUrl, log });
    log("bundled stack ready");
  } catch (error) {
    log("bundle start failed:", error);
  }
} else if (skipBundle) {
  log("TRACERA_SKIP_BUNDLE=1 - not starting bundled stack");
} else {
  log("rich gateway mode - stack is managed externally");
}

let win: BrowserWindow;
const rpc = defineElectrobunRPC<{ bun: BunRequests; webview: WebviewRequests }>("bun", {
  handlers: {
    requests: {
      getTargetUrl: () => targetUrl,
      getVersion: () => APP_VERSION,
      reload: () => win.webview.loadURL(targetUrl),
    },
  },
});

win = new BrowserWindow({
  title: "Tracera",
  frame: { x: 100, y: 100, width: 1440, height: 920 },
  url: targetUrl,
  titleBarStyle: "hiddenInset",
  rpc,
});
log("window created, id=", win.id);

const tray = new Tray({ title: "Tracera" });
const menu: MenuItemConfig[] = [
  { type: "normal", label: "Show Tracera", action: "show-window" },
  { type: "separator" },
  { type: "normal", label: "Reload", action: "reload-window" },
  { type: "separator" },
  { type: "normal", label: `Target: ${targetUrl}`, enabled: false },
  { type: "separator" },
  { type: "normal", label: "Quit Tracera", action: "quit" },
];
tray.setMenu(menu);
tray.on("tray-clicked", (event: unknown) => {
  const action = (event as { action?: string } | null)?.action ?? "";
  if (action === "reload-window") win.webview.loadURL(targetUrl);
  else if (action === "quit") process.emit("SIGTERM");
  else win.show();
});
log("tray created, id=", tray.id);

const shutdown = async () => {
  if (!stopBundle) return;
  try {
    await stopBundle();
  } catch (error) {
    log("bundle shutdown failed:", error);
  }
  stopBundle = undefined;
};
process.once("SIGTERM", () => void shutdown().finally(() => process.exit(0)));
process.once("SIGINT", () => void shutdown().finally(() => process.exit(130)));
process.on("beforeExit", () => tray.remove());
