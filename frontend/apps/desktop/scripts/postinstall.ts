/**
 * scripts/postinstall.ts — run by `bun install` via `"postinstall"` in package.json.
 *
 * Problem: electrobun downloads its CLI binary lazily (on first invocation of
 * `bunx electrobun`), but on macOS the freshly downloaded binary may have an
 * invalid code signature, causing macOS to kill it with SIGKILL (exit 137)
 * without any output — so `bunx electrobun build` silently does nothing.
 *
 * This is an upstream electrobun issue (confirmed v1.18.1): the tar-extracted
 * binary loses or invalidates its ad-hoc signature during the Node.js
 * copyFileSync step in the CJS wrapper (the copy touches mtime/xattr in a
 * way that macOS's code-signature verifier rejects).
 *
 * Fix strategy:
 *   1. Eagerly trigger the electrobun CLI binary download (run the CJS
 *      bootstrap with a no-op subcommand so it downloads to .cache + bin).
 *   2. Ad-hoc re-sign both the .cache and bin copies with
 *      `codesign --sign - --force` (no Apple Developer cert required;
 *      Gatekeeper accepts ad-hoc signatures for local-dev builds).
 *
 * Non-macOS: download step still runs (harmless), codesign step is skipped.
 * SKIP_POSTINSTALL=1: bypass entirely (CI environments that run on Linux
 * where Gatekeeper does not apply and codesign is unavailable).
 */

import { join } from "path";
import { existsSync } from "fs";

const DESKTOP_DIR = import.meta.dir.replace(/[/\\]scripts$/, "");
const ELECTROBUN_DIR = join(DESKTOP_DIR, "node_modules", "electrobun");
const CJS_WRAPPER = join(ELECTROBUN_DIR, "bin", "electrobun.cjs");
const BIN_PATH = join(ELECTROBUN_DIR, "bin", "electrobun");
const CACHE_PATH = join(ELECTROBUN_DIR, ".cache", "electrobun");

function log(...args: unknown[]): void {
  process.stdout.write(`[postinstall] ${args.join(" ")}\n`);
}

async function ensureElectrobunBinary(): Promise<void> {
  if (existsSync(BIN_PATH)) {
    log(`electrobun binary already present at ${BIN_PATH}`);
    return;
  }

  log("triggering electrobun CLI download via CJS bootstrap…");

  // Run the CJS wrapper with a dummy subcommand that causes it to
  // download the CLI binary and exit.  The wrapper exits 0 even if
  // the spawned binary fails (which it will — it's unsigned).
  // We only need the download side-effect.
  const proc = Bun.spawn(
    ["node", CJS_WRAPPER, "download-only-__noop__"],
    {
      cwd: DESKTOP_DIR,
      stdout: "pipe",
      stderr: "pipe",
      env: { ...process.env },
    },
  );
  const [stdout, stderr] = await Promise.all([
    new Response(proc.stdout as ReadableStream).text(),
    new Response(proc.stderr as ReadableStream).text(),
    proc.exited,
  ]);
  const combined = (stdout + stderr).trim();
  if (combined) log(combined);

  if (!existsSync(BIN_PATH)) {
    // The CJS wrapper may not have copied from .cache → bin on this run.
    // That is fine; we sign whichever file exists below.
    log("note: bin not populated after bootstrap (will be created on first bunx electrobun call)");
  }
}

async function resign(binPath: string): Promise<boolean> {
  log(`ad-hoc codesign: ${binPath}`);
  const proc = Bun.spawn(
    ["codesign", "--sign", "-", "--force", binPath],
    { stdout: "pipe", stderr: "pipe" },
  );
  const [_out, stderr, code] = await Promise.all([
    new Response(proc.stdout as ReadableStream).text(),
    new Response(proc.stderr as ReadableStream).text(),
    proc.exited,
  ]);
  if (code !== 0) {
    log(`codesign exit ${code}: ${stderr.trim()}`);
    return false;
  }
  log(`codesign: signed successfully`);
  return true;
}

async function main(): Promise<void> {
  if (process.env.SKIP_POSTINSTALL === "1") {
    log("SKIP_POSTINSTALL=1 — skipping");
    return;
  }

  // Eagerly download the binary so we can sign it.
  await ensureElectrobunBinary();

  // macOS-only: re-sign to fix invalid-signature SIGKILL.
  if (process.platform !== "darwin") {
    log("non-macOS — codesign step skipped");
    return;
  }

  let anyFound = false;
  for (const p of [CACHE_PATH, BIN_PATH]) {
    if (existsSync(p)) {
      anyFound = true;
      await resign(p);
    }
  }

  if (!anyFound) {
    // Download did not happen (possibly no network in this environment).
    // The first real `bunx electrobun build` will download and then fail
    // with SIGKILL on macOS.  Print a clear diagnostic.
    log(
      "WARNING: electrobun binary not found after download attempt.\n" +
      "[postinstall] On macOS, run: codesign --sign - --force node_modules/electrobun/bin/electrobun\n" +
      "[postinstall] after the binary is present (after first `bunx electrobun build` attempt).",
    );
  }
}

main().catch((err: unknown) => {
  // Never fail bun install over this — log and exit 0
  const msg = err instanceof Error ? err.message : String(err);
  process.stdout.write(`[postinstall] warning: ${msg}\n`);
});
