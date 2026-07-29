/**
 * Tracera desktop — bundled-stack lifecycle.
 *
 * The Tracera.app bundle ships a `tracera` CLI binary that wraps Compose
 * across Apple Container / Docker / Podman / WSL2. The desktop shell invokes
 * it on launch to bring the cluster up and on quit to tear it down. We
 * keep a TS-side wrapper so the existing RPC surface stays unchanged.
 *
 * The CLI's `bin/tracera` binary is found by walking up from the running
 * process's `import.meta.dir` to the bundle root. In development (no .app
 * bundle) the path falls back to the source-tree target directory.
 */

import { existsSync } from "node:fs";
import { join } from "node:path";

export const LOCAL_PORT = 18081;
export const LOCAL_URL = `http://127.0.0.1:${LOCAL_PORT}`;

export type CommandRunner = (
  command: string[],
  options: { cwd: string; env: Record<string, string | undefined> },
) => { exited: Promise<number>; kill: () => void; stdout?: ReadableStream<Uint8Array> | null };

export type BundleOptions = {
  /** Override path to the bundled CLI binary. */
  cliPath?: string;
  /** Override the local URL the bundle reports. */
  localUrl?: string;
  /** Logger. */
  log?: (...args: unknown[]) => void;
  /** Custom runner (test injection). */
  run?: CommandRunner;
  /** Override fetch for tests. */
  fetchImpl?: typeof fetch;
  /** Override sleep for tests. */
  sleep?: (milliseconds: number) => Promise<void>;
  /** Readiness timeout (ms). */
  timeoutMs?: number;
};

type ReadinessPayload = { status?: string };

/** Probe both service gates used by the bundled stack.
 *
 * A successful TCP response is not sufficient for desktop startup: the
 * frontend can answer before migrations and dependent services are ready.
 * Keep this helper injectable so startup tests exercise the exact gate.
 */
export async function probeBundleReady(
  url: string,
  fetchImpl: typeof fetch,
): Promise<boolean> {
  const [health, ready] = await Promise.all([
    fetchImpl(`${url.replace(/\/$/, "")}/health`),
    fetchImpl(`${url.replace(/\/$/, "")}/ready`),
  ]);
  if (!health.ok || !ready.ok) return false;
  const [healthBody, readyBody] = (await Promise.all([
    health.json(),
    ready.json(),
  ])) as [ReadinessPayload, ReadinessPayload];
  return healthBody.status === "ok" && readyBody.status === "ready";
}

/**
 * Resolve the path to the bundled `tracera` CLI. Walks up from `import.meta.dir`
 * looking for the bundle layout created by `bunx electrobun build` and the
 * `scripts/launch.sh` wrapper.
 */
export function resolveBundleCli(startDir: string): string | null {
  const candidates = [
    // Production: Tracera.app/Contents/Resources/tracera-bundle/bin/tracera
    join(startDir, "..", "..", "Resources", "tracera-bundle", "bin", "tracera"),
    // Dev: scripts/run-bundled-cli.ts invoked from frontend/apps/desktop
    join(startDir, "..", "..", "..", "..", "target", "release", "tracera"),
    join(startDir, "..", "..", "..", "..", "target", "debug", "tracera"),
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return null;
}
function defaultRunner(
  command: string[],
  options: { cwd: string; env: Record<string, string | undefined> },
) {
  return Bun.spawn(command, {
    cwd: options.cwd,
    env: options.env,
    stdout: "pipe",
    stderr: "pipe",
  });
}
/**
 * Start the bundled Tracera stack. Resolves when /health is OK.
 * Returns a stop() that tears the stack down.
 */
export async function startBundle(opts: BundleOptions = {}): Promise<() => Promise<void>> {
  const log = opts.log ?? (() => {});
  const run = opts.run ?? defaultRunner;
  const sleep = opts.sleep ?? ((ms) => new Promise((r) => setTimeout(r, ms)));
  const fetchImpl = opts.fetchImpl ?? fetch;
  const cliPath = opts.cliPath ?? resolveBundleCli(import.meta.dir);
  if (!cliPath) throw new Error("bundled tracera CLI not found — rebuild the .app or run `cargo build --release -p tracera-cli`");

  const env = { ...process.env };
  log("bundled CLI:", cliPath);
  const up = run([cliPath, "up", "--no-wait"], { cwd: process.cwd(), env });
  const exitCode = await up.exited;
  if (exitCode !== 0) throw new Error(`tracera up failed with exit code ${exitCode}`);

  const url = opts.localUrl ?? LOCAL_URL;
  const timeoutMs = opts.timeoutMs ?? 180_000;
  const deadline = Date.now() + timeoutMs;
  let delayMs = 250;
  while (Date.now() < deadline) {
    try {
      if (await probeBundleReady(url, fetchImpl)) break;
    } catch (error) {
      log("bundle readiness probe failed; retrying:", error);
    }
    await sleep(Math.min(delayMs, Math.max(0, deadline - Date.now())));
    delayMs = Math.min(delayMs * 2, 2000);
  }
  if (!(await probeBundleReady(url, fetchImpl).catch(() => false))) {
    throw new Error(`bundled stack did not pass /health and /ready within ${timeoutMs}ms at ${url}`);
  }

  return async () => {
    const down = run([cliPath, "down"], { cwd: process.cwd(), env });
    const code = await down.exited;
    if (code !== 0) throw new Error(`tracera down failed with exit code ${code}`);
  };
}
