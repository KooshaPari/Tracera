#!/usr/bin/env bun
/**
 * Prepare an electron-builder staging directory from an existing electrobun
 * build output. Mirrors scripts/build.mjs in AgilePlus-desktop; copied rather
 * than shared because the two repos don't share node_modules and we want a
 * 1:1 runbook per repo.
 *
 * Staged dir layout expected by electron-builder:
 *   stage/
 *     Tracera.exe              (renamed copy of bin/launcher.exe)
 *     bin/launcher.exe         (Electrobun native launcher)
 *     Info.plist
 *     lib/                     (CEF / runtime libs)
 *     Resources/app/           (Bun-side code, views, assets)
 */
import { existsSync, mkdirSync, cpSync, rmSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { platform, arch } from "node:process";

const projectRoot = resolve(import.meta.dir, "..");
const buildDir = join(projectRoot, "build");
const stageDir = join(projectRoot, "stage");

const plat = platform === "win32" ? "win" : platform === "darwin" ? "mac" : "linux";
const archName = arch === "x64" ? "x64" : arch === "arm64" ? "arm64" : arch;
const platAliases = platform === "darwin" ? [plat, "macos"] : [plat];

let srcDir: string | null = null;
for (const p of platAliases) {
  const candidate = join(buildDir, `dev-${p}-${archName}`);
  if (existsSync(candidate)) {
    srcDir = candidate;
    break;
  }
}

if (srcDir === null) {
  const suffixes = platAliases.map((p) => `dev-${p}-${archName}`).join(", ");
  console.error(`[prepare-bundle] electrobun build output not found. Checked: ${suffixes}.`);
  console.error(`[prepare-bundle] Available entries in build/: ${readdirSync(buildDir).join(", ")}`);
  console.error(`[prepare-bundle] Run \`bun run build\` first.`);
  process.exit(1);
}

const candidates = readdirSync(srcDir).filter((n) => n.endsWith("-dev") || n.endsWith(".app"));
if (candidates.length === 0) {
  console.error(`[prepare-bundle] no .app or *-dev artifact found under ${srcDir}.`);
  process.exit(1);
}
const appDir = join(srcDir, candidates.sort()[0]);

if (existsSync(stageDir)) rmSync(stageDir, { recursive: true, force: true });
mkdirSync(stageDir, { recursive: true });

cpSync(appDir, stageDir, { recursive: true });

// electron-builder on Windows looks up <productName>.exe at the staging root.
// Our launcher is literally `launcher.exe`, so we stage a renamed copy.
const productName = "Tracera";
const launcherSrc = join(stageDir, "bin", "launcher.exe");
if (existsSync(launcherSrc)) {
  cpSync(launcherSrc, join(stageDir, `${productName}.exe`));
}

console.log(`[prepare-bundle] staged ${appDir} -> ${stageDir}`);
