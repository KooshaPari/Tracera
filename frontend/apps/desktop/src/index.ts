/**
 * Tracera desktop entry — Electrobun BrowserWindow launcher.
 *
 * Default: the bundled local stack (Tracera.app/Contents/Resources/tracera-bundle/).
 * Opt-in hosted: set TRACERA_URL or TRACERA_HOSTED_URL in the environment.
 *
 * On startup we call `startBundle()` which invokes the bundled `tracera` CLI to
 * bring the compose stack up and waits for /health to return ok before opening
 * the BrowserWindow.  The CLI auto-detects apple-container | docker | podman |
 * wsl+docker and falls back gracefully.
 */
import { app, BrowserWindow } from "electron";
import { startBundle } from "./bundle";
import { resolveTargetUrl } from "./target";

let stopBundle: (() => Promise<void>) | null = null;

async function main() {
  const targetUrl = resolveTargetUrl(process.env);

  // Auto-start the bundled stack for local URLs unless explicitly skipped.
  const isLocal = targetUrl.startsWith("http://127.0.0.1");
  const skipBundle = process.env.TRACERA_SKIP_BUNDLE === "1";
  if (isLocal && !skipBundle) {
    console.log("[tracera-desktop] starting bundled stack ...");
    try {
      stopBundle = await startBundle({
        log: (...args) => console.log("[tracera-desktop]", ...args),
      });
      console.log("[tracera-desktop] bundled stack healthy.");
    } catch (err) {
      console.error("[tracera-desktop] bundled stack failed to start:", err);
      // Fall through — the window will open but may show a connection error.
    }
  }

  console.log("[tracera-desktop] target URL:", targetUrl);
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    title: "Tracera",
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadURL(targetUrl);
  win.on("closed", () => {
    app.quit();
  });
}

app.on("ready", () => {
  main().catch((err) => {
    console.error("[tracera-desktop] fatal:", err);
    app.quit();
  });
});

app.on("window-all-closed", async () => {
  if (stopBundle) {
    try {
      await stopBundle();
    } catch {
      /* best-effort */
    }
  }
  app.quit();
});
