import { app, BrowserWindow, ipcMain, shell } from "electron";
import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const DEFAULT_GATEWAY = "http://127.0.0.1:18000";
const gateway = (process.env.TRACERA_GATEWAY_URL || process.env.TRACERA_URL || DEFAULT_GATEWAY).replace(/\/$/, "");
const cliPath = process.env.TRACERA_CLI_PATH || join(process.resourcesPath, "tracera-bundle", "bin", "tracera");
let cli: ChildProcess | undefined;

async function waitForGateway(timeoutMs = 180_000): Promise<boolean> {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) {
    try {
      const response = await fetch(`${gateway}/health`, { signal: AbortSignal.timeout(2500) });
      if (response.ok) return true;
    } catch { /* service is still starting */ }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  return false;
}

async function startServices(): Promise<void> {
  if (process.env.TRACERA_AUTOSTART === "0" || !existsSync(cliPath)) return;
  cli = spawn(cliPath, ["up", "--no-wait"], { stdio: "inherit", env: process.env });
  const code = await new Promise<number>((resolve) => cli?.once("exit", (value) => resolve(value ?? 1)));
  if (code !== 0) throw new Error(`tracera up exited with ${code}`);
  if (!(await waitForGateway())) throw new Error(`gateway did not become ready at ${gateway}`);
}

function createWindow(): BrowserWindow {
  const window = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1024,
    minHeight: 700,
    show: false,
    webPreferences: { preload: join(__dirname, "preload.cjs"), contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  window.once("ready-to-show", () => window.show());
  window.webContents.setWindowOpenHandler(({ url }) => { void shell.openExternal(url); return { action: "deny" }; });
  const embeddedIndex = join(__dirname, "web", "index.html");
  if (process.env.TRACERA_DEV_URL) void window.loadURL(process.env.TRACERA_DEV_URL);
  else if (existsSync(embeddedIndex)) void window.loadFile(embeddedIndex);
  else void window.loadURL(gateway);
  return window;
}

app.whenReady().then(async () => {
  try { await startServices(); } catch (error) { console.error("[tracera] startup failed", error); }
  createWindow();
  ipcMain.handle("tracera:gateway", () => gateway);
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
app.on("before-quit", () => { if (cliPath && cli) spawn(cliPath, ["down"], { stdio: "ignore", env: process.env }); });
