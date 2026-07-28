#!/usr/bin/env bun
/**
 * Tracera desktop — Electrobun main-process entry point.
 *
 * On launch the bundled CLI brings up the local compose stack (postgres +
 * tracera-server + frontend-nginx) and we wait until /health returns ok.
 * The BrowserWindow then opens at the resolved target URL.
 *
 * TRACERA_URL env var overrides the default for pointing at staging
 * or other deployments. TRACERA_SKIP_BUNDLE=1 disables auto-start.
 */

import { resolveBundleCli, startBundle, LOCAL_URL } from "./bundle.js";
import { resolveTargetUrl } from "./target.js";

const log = (...args: unknown[]) => console.log("[tracera-desktop]", ...args);

const targetUrl = resolveTargetUrl(process.env);
log("target URL:", targetUrl);

const isPackaged = !!resolveBundleCli(import.meta.dir);
const skipBundle = process.env.TRACERA_SKIP_BUNDLE === "1";

// The bundled CLI serves legacy 18081; canonical rich gateway 18000 is external.
if (isPackaged && !skipBundle && targetUrl.startsWith(LOCAL_URL)) {
  try {
    log("starting bundled stack…");
    const stop = await startBundle({ localUrl: targetUrl, log });
    log("bundled stack ready");

    // Expose shutdown hook for Electrobun lifecycle
    globalThis.__traceraStop = stop;
  } catch (err) {
    log("bundle start failed:", err);
    // Fall through — the BrowserWindow will open and show the error
  }
} else if (skipBundle) {
  log("TRACERA_SKIP_BUNDLE=1 — not starting bundled stack");
} else {
  log("no bundled CLI found — not starting stack (dev mode)");
}
