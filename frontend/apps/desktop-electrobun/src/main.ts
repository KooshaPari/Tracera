/**
 * Tracera Electrobun main process
 *
 * Responsibilities:
 *  1. Boot services via `process-compose up -d` (one-click service start)
 *  2. Open main BrowserWindow pointing at @tracertm/web renderer
 *  3. Expose a minimal RPC surface matching the old Electron preload API
 */
import { BrowserWindow, ApplicationMenu } from "electrobun/bun";
import { $ } from "bun";
import { join } from "node:path";

// ── 1. Resolve renderer URL ──────────────────────────────────────────────────
// Dev:  set TRACERTM_RENDERER_URL=http://localhost:3000
// Prod: load bundled views://web/index.html
const RENDERER_URL =
  process.env.TRACERTM_RENDERER_URL ?? "views://web/index.html";

// ── 2. One-click service boot ────────────────────────────────────────────────
async function bootServices(): Promise<void> {
  // Resolve repo root: desktop-electrobun is at frontend/apps/desktop-electrobun
  // process-compose.yml lives at repo root (4 levels up)
  const repoRoot = join(import.meta.dir, "..", "..", "..", "..");

  console.log("[TraceRTM] Booting services via process-compose…");
  try {
    const result =
      await $`process-compose up -d --config ${join(repoRoot, "process-compose.yml")}`.quiet();
    console.log("[TraceRTM] process-compose:", result.text());
  } catch (err) {
    // Non-fatal: services may already be running, or process-compose not in PATH
    console.warn(
      "[TraceRTM] process-compose boot skipped (not found or already running):",
      (err as Error).message
    );
  }
}

// ── 3. Create main window ────────────────────────────────────────────────────
function createMainWindow(): BrowserWindow {
  const win = new BrowserWindow({
    title: "TraceRTM",
    url: RENDERER_URL,
    frame: {
      width: 1400,
      height: 900,
    },
    titleBarStyle: "hiddenInset",
  });

  return win;
}

// ── 4. Application menu ──────────────────────────────────────────────────────
function setupMenu(win: BrowserWindow): void {
  // Electrobun ApplicationMenu uses a declarative array of MenuItems.
  // We mirror the structure from the old Electron shell.
  ApplicationMenu.setApplicationMenu([
    {
      label: "TraceRTM",
      submenu: [
        { role: "about" },
        { type: "separator" },
        { role: "services" },
        { type: "separator" },
        { role: "hide" },
        { role: "hideOthers" },
        { role: "unhide" },
        { type: "separator" },
        { role: "quit" },
      ],
    },
    {
      label: "File",
      submenu: [
        {
          label: "New Project",
          accelerator: "CmdOrCtrl+N",
          click: () => win.webview.executeJavaScript("window.__tracertm?.onNewProject?.()"),
        },
        {
          label: "Open Project",
          accelerator: "CmdOrCtrl+O",
          click: () => win.webview.executeJavaScript("window.__tracertm?.onOpenProject?.()"),
        },
        { type: "separator" },
        {
          label: "Import…",
          click: () => win.webview.executeJavaScript("window.__tracertm?.onImport?.()"),
        },
        {
          label: "Export…",
          click: () => win.webview.executeJavaScript("window.__tracertm?.onExport?.()"),
        },
      ],
    },
    {
      label: "Edit",
      submenu: [
        { role: "undo" },
        { role: "redo" },
        { type: "separator" },
        { role: "cut" },
        { role: "copy" },
        { role: "paste" },
        { role: "selectAll" },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { role: "toggleDevTools" },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
    {
      label: "Window",
      submenu: [{ role: "minimize" }, { role: "zoom" }, { type: "separator" }, { role: "front" }],
    },
    {
      label: "Help",
      submenu: [
        {
          label: "Documentation",
          click: () => {
            // open in system browser
            $`open https://tracertm.dev/docs`.nothrow().quiet();
          },
        },
        {
          label: "Report Issue",
          click: () => {
            $`open https://github.com/KooshaPari/Tracera/issues`.nothrow().quiet();
          },
        },
      ],
    },
  ]);
}

// ── 5. Bootstrap ─────────────────────────────────────────────────────────────
async function main(): Promise<void> {
  // Boot services first (non-blocking on failure)
  await bootServices();

  const win = createMainWindow();
  setupMenu(win);

  console.log(`[TraceRTM] Desktop launched → ${RENDERER_URL}`);
}

main().catch((err) => {
  console.error("[TraceRTM] Fatal startup error:", err);
  process.exit(1);
});
