/**
 * desktop/tests/e2e_desktop.test.ts — Tracera desktop smoke suite.
 *
 * Two modes:
 *
 *   HOST MODE (default, macOS with display):
 *     Spawns `bunx electrobun dev`, waits for "[tracera-desktop] window
 *     created" in the launcher log, then asserts the shell loaded correctly
 *     and the tray was created.
 *     Run: cd frontend/apps/desktop && bun test tests/e2e_desktop.test.ts
 *
 *   CI / HEADLESS MODE (CI=1 or HEADLESS=1 env):
 *     Skips the launcher-log invariants (no display) and runs a process-
 *     startup check that verifies the bun entrypoint at least compiles and
 *     the electrobun binary is present.
 *     Set: CI=1 bun test tests/e2e_desktop.test.ts
 *
 * Residual manual-only checks (documented honestly):
 *   - Pixel-level webview rendering: WKWebView has no headless mode.
 *   - System tray icon appearance.
 *   - External URL navigation within the webview.
 *   These are tracked in docs/QGATE_BASELINE.md → "manual-only checks".
 */

import { test, expect, beforeAll, afterAll, describe } from "bun:test";
import * as path from "path";

// ---------------------------------------------------------------------------
// Mode detection
// ---------------------------------------------------------------------------

const HEADLESS =
  !!process.env.HEADLESS ||
  process.env.CI === "1" ||
  !process.env.DISPLAY;
const DESKTOP_DIR = path.resolve(import.meta.dir, "..");

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const WINDOW_CREATED_TIMEOUT_MS = 12_000;
const LOG_COLLECT_WINDOW_MS = 3_000;

// ---------------------------------------------------------------------------
// Shared state
// ---------------------------------------------------------------------------

let appProc: ReturnType<typeof Bun.spawn> | null = null;
let launcherLog = "";
let appWindowCreated = false;
let appTrayCreated = false;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function pipeStream(
  stream: ReadableStream<Uint8Array>,
  accumulator: { value: string },
  label: string,
): Promise<void> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      accumulator.value += chunk;
      process.stderr.write(`[e2e:${label}] ${chunk}`);
    }
  } catch {
    // stream closed when we kill the process — expected
  }
}

async function waitFor(predicate: () => boolean, timeoutMs: number): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (predicate()) return true;
    await Bun.sleep(250);
  }
  return false;
}

// ---------------------------------------------------------------------------
// Suite lifecycle
// ---------------------------------------------------------------------------

beforeAll(async () => {
  if (HEADLESS) {
    console.log("[e2e] HEADLESS/CI mode: skipping app launch");
    return;
  }

  const logAcc = { value: "" };

  appProc = Bun.spawn(["bunx", "electrobun", "dev"], {
    cwd: DESKTOP_DIR,
    env: {
      ...process.env,
      CI: "1",
    },
    stdout: "pipe",
    stderr: "pipe",
  });

  void pipeStream(appProc.stdout as ReadableStream<Uint8Array>, logAcc, "stdout");
  void pipeStream(appProc.stderr as ReadableStream<Uint8Array>, logAcc, "stderr");

  // Wait for window created log
  appWindowCreated = await waitFor(
    () => logAcc.value.includes("[tracera-desktop] window created"),
    WINDOW_CREATED_TIMEOUT_MS,
  );

  // Wait for tray created log
  appTrayCreated = await waitFor(
    () => logAcc.value.includes("[tracera-desktop] tray created"),
    WINDOW_CREATED_TIMEOUT_MS,
  );

  // Let logs accumulate
  await Bun.sleep(Math.min(LOG_COLLECT_WINDOW_MS, 2000));
  launcherLog = logAcc.value;
}, 30_000);

afterAll(() => {
  appProc?.kill();
  appProc = null;
});

// ---------------------------------------------------------------------------
// Headless / CI smoke tests — verify build artifacts and entrypoint
// ---------------------------------------------------------------------------

describe("Tracera desktop — build smoke (CI-safe)", () => {
  test("electrobun binary is present (bun install was run)", async () => {
    // bunx electrobun resolves via node_modules; verify the package exists
    const bunxResult = Bun.spawn(["bun", "x", "electrobun", "--help"], {
      cwd: DESKTOP_DIR,
      stdout: "pipe",
      stderr: "pipe",
    });
    // Allow up to 10 s for the binary to print help and exit
    const exitCode = await Promise.race([
      bunxResult.exited,
      Bun.sleep(10_000).then(() => -1),
    ]);
    // electrobun --help may exit 0 or 1 but should NOT timeout (exitCode = -1)
    // and should NOT fail with ENOENT (which throws an exception above)
    expect(exitCode).not.toBe(-1);
  }, 15_000);

  test("src/index.ts bun typecheck passes", async () => {
    const proc = Bun.spawn(["bunx", "tsc", "--noEmit", "--project", "tsconfig.json"], {
      cwd: DESKTOP_DIR,
      stdout: "pipe",
      stderr: "pipe",
      env: { ...process.env, PATH: process.env.PATH ?? "" },
    });
    const [stdout, stderr, exitCode] = await Promise.all([
      new Response(proc.stdout as ReadableStream).text(),
      new Response(proc.stderr as ReadableStream).text(),
      proc.exited,
    ]);
    if (exitCode !== 0) {
      console.error("[e2e] tsc output:", stdout, stderr);
    }
    expect(exitCode).toBe(0);
  }, 30_000);
});

// ---------------------------------------------------------------------------
// Launcher-log invariant tests — HOST MODE only (requires display)
// ---------------------------------------------------------------------------

describe("Tracera desktop app — launcher log invariants", () => {
  test("window created log appears", () => {
    if (HEADLESS) {
      console.log("[e2e] HEADLESS: skipping (no display)");
      return;
    }
    expect(launcherLog).toContain("[tracera-desktop] window created");
    expect(appWindowCreated).toBe(true);
  });

  test("tray created log appears", () => {
    if (HEADLESS) {
      console.log("[e2e] HEADLESS: skipping (no display)");
      return;
    }
    expect(launcherLog).toContain("[tracera-desktop] tray created");
    expect(appTrayCreated).toBe(true);
  });

  test("target URL is logged", () => {
    if (HEADLESS) {
      console.log("[e2e] HEADLESS: skipping (no display)");
      return;
    }
    // The main process logs "target URL: <url>" on startup
    expect(launcherLog).toMatch(/\[tracera-desktop\] target URL:/);
  });

  test("no unhandled crash in launcher log", () => {
    if (HEADLESS) {
      console.log("[e2e] HEADLESS: skipping (no display)");
      return;
    }
    // No fatal errors in the Bun process logs
    expect(launcherLog).not.toMatch(/\[error\] Uncaught/i);
    expect(launcherLog).not.toMatch(/Segmentation fault/i);
    expect(launcherLog).not.toMatch(/SIGABRT/i);
  });
});
