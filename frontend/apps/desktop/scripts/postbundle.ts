/**
 * scripts/postbundle.ts — runs after `bunx electrobun build` to bundle the
 * native `tracera` CLI + an image-based compose file + a PATH-aware wrapper
 * into the produced `.app` at `Contents/Resources/tracera-bundle/`.
 *
 * Without this step, the desktop app would load an external URL and depend
 * on the user running `docker compose` by hand. With this step, the .app is
 * self-contained: the bundled CLI auto-detects the host's container runtime
 * (apple-container / docker / podman / wsl+docker) and drives Compose on
 * launch and quit.
 *
 * Idempotent — re-running overwrites the bundle contents in place. The
 * script exits non-zero only if the CLI binary is missing (because the user
 * hasn't run `cargo build --release -p tracera-cli` yet).
 */
import { join, dirname } from "node:path";
import { existsSync, mkdirSync, rmSync, copyFileSync, cpSync, chmodSync, writeFileSync, renameSync, readFileSync } from "node:fs";

const DESKTOP_DIR = import.meta.dir.replace(/[/\\]scripts$/, "");
const REPO_ROOT = join(DESKTOP_DIR, "..", "..", "..");
const CLI_SRC = join(REPO_ROOT, "target", "release", "tracera");
const FRONTEND_DIST = join(REPO_ROOT, "frontend", "dist");

function log(...args: unknown[]): void {
  process.stdout.write(`[postbundle] ${args.join(" ")}\n`);
}

function findApp(): string | null {
  const buildDir = join(DESKTOP_DIR, "build");
  const platform = process.platform === "darwin"
    ? `dev-${process.arch === "arm64" ? "macos-arm64" : "macos-x64"}`
    : `dev-${process.platform}-${process.arch}`;
  const candidates = [
    join(buildDir, platform, "Tracera.app"),
    join(buildDir, platform, "Tracera-dev.app"),
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return null;
}

const COMPOSE_BUNDLE = `name: tracera-bundle

# Tracera bundled stack — image-based compose consumed by \`bin/tracera\`.
#
# Generated at .app build time and embedded into
# \`Tracera.app/Contents/Resources/tracera-bundle/docker-compose.bundle.yml\`.
# The bundled CLI manages it from
# \`~/Library/Application Support/Tracera/\` (or the repo root when run
# standalone). Service names match the legacy local stack so the frontend
# nginx (baked into the frontend image at build time) can resolve
# \`tracera-server\` via compose DNS.

services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    env_file:
      - .env.local
    environment:
      POSTGRES_USER: tracera
      POSTGRES_DB: tracera
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracera -d tracera"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - tracera_postgres_data:/var/lib/postgresql/data

  tracera-server:
    image: tracera-tracera-server:latest
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - .env.local
    environment:
      TRACERA_DB_BACKEND: postgres
      TRACERA_BIND: 0.0.0.0:8080
      TRACERA_TRUSTED_PROXY: "true"
      DATABASE_URL: postgres://tracera:\${POSTGRES_PASSWORD}@postgres:5432/tracera
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:8080/health | grep -q ok"]
      interval: 5s
      timeout: 5s
      retries: 20

  frontend:
    image: tracera-frontend:latest
    restart: unless-stopped
    depends_on:
      tracera-server:
        condition: service_healthy
    ports:
      - "\${TRACERA_LOCAL_BIND_ADDR:-127.0.0.1}:\${TRACERA_LOCAL_PORT:-18081}:80"

volumes:
  tracera_postgres_data:
    name: tracera_bundle_postgres_data
`;

const LAUNCH_SH = `#!/usr/bin/env bash
# Tracera desktop — bundled-stack lifecycle wrapper.
#
# Sets a sensible PATH (Finder-launched processes get a stripped env) and
# forwards everything to the bundled \`bin/tracera\` CLI which manages the
# Compose stack across apple-container / docker / podman / wsl+docker.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "\${BASH_SOURCE[0]}")" && pwd)"
CLI="\$SCRIPT_DIR/../bin/tracera"

if [[ ! -x "\$CLI" ]]; then
  echo "[tracera-desktop] bundled CLI missing at \$CLI" >&2
  exit 127
fi

export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:\$PATH"

exec "\$CLI" "\$@"
`;

const README = `Tracera desktop — bundled stack
====================================

This directory is the self-contained backend that \`Tracera.app\` brings up
on launch. The \`bin/tracera\` CLI is a Rust binary that
auto-detects the host's container runtime (apple-container > docker >
podman > wsl+docker) and drives Compose via that runtime.

Layout:
  bin/tracera                    native CLI; auto-detects runtime
  docker-compose.bundle.yml      image-based stack consumed by the CLI
  scripts/launch.sh              PATH-aware wrapper used by the .app

State files written at runtime (under \`~/Library/Application Support/Tracera/\`):
  .env.local                     POSTGRES_PASSWORD + bind port
  tracera_postgres_data/         bind-mounted postgres volume
`;

async function main(): Promise<void> {
  if (!existsSync(CLI_SRC)) {
    process.stderr.write(
      `[postbundle] ERROR: native CLI missing at ${CLI_SRC}.\n` +
      `[postbundle] Run \`cargo build --release -p tracera-cli\` from the repo root, then re-run \`bunx electrobun build\`.\n`,
    );
    process.exit(1);
  }

  const app = findApp();
  if (!app) {
    log("no .app produced yet — skipping bundle (this is fine on dev platforms)");
    return;
  }

  // Electrobun's CLI emits `Tracera-dev.app` for the dev profile and `Tracera.app`
  // for production; we always want the final bundle named `Tracera.app` with the
  // matching CFBundleName so the launcher's Info.plist reads cleanly when copied
  // into /Applications.
  const devApp = join(dirname(app), "Tracera-dev.app");
  let finalApp = app;
  if (app.endsWith("Tracera-dev.app") || existsSync(devApp)) {
    if (existsSync(devApp) && !existsSync(app)) {
      renameSync(devApp, app);
      finalApp = app;
      log(`renamed ${devApp} → ${app}`);
    } else if (app.endsWith("Tracera-dev.app") && !existsSync(join(dirname(app), "Tracera.app"))) {
      renameSync(app, join(dirname(app), "Tracera.app"));
      finalApp = join(dirname(app), "Tracera.app");
      log(`renamed ${app} → ${finalApp}`);
    } else {
      finalApp = join(dirname(app), "Tracera.app");
    }
  }

  const plistPath = join(finalApp, "Contents", "Info.plist");
  if (existsSync(plistPath)) {
    const body = readFileSync(plistPath, "utf8");
    if (/<key>CFBundleName<\/key>\s*<string>Tracera-dev<\/string>/.test(body)) {
      const patched = body.replace(
        /<key>CFBundleName<\/key>\s*<string>Tracera-dev<\/string>/,
        "<key>CFBundleName</key><string>Tracera</string>",
      );
      writeFileSync(plistPath, patched, "utf8");
      log(`patched CFBundleName → Tracera in ${plistPath}`);
    }
  }

  const bundle = join(finalApp, "Contents", "Resources", "tracera-bundle");
  const resources = join(finalApp, "Contents", "Resources");
  const binDir = join(bundle, "bin");
  const scriptsDir = join(bundle, "scripts");

  rmSync(bundle, { recursive: true, force: true });
  mkdirSync(binDir, { recursive: true });
  mkdirSync(scriptsDir, { recursive: true });

  // Ship the built SPA alongside the shell. This keeps the installed artifact
  // self-describing and makes the web UI available even when no source checkout
  // is present next to the app.
  if (!existsSync(join(FRONTEND_DIST, "index.html"))) {
    throw new Error(`frontend build missing at ${FRONTEND_DIST}; run the web build first`);
  }
  cpSync(FRONTEND_DIST, resources, { recursive: true, force: true });
  log(`bundled frontend → ${resources}`);

  // CLI binary
  copyFileSync(CLI_SRC, join(binDir, "tracera"));
  chmodSync(join(binDir, "tracera"), 0o755);
  log(`bundled CLI → ${join(binDir, "tracera")}`);

  // Compose file (image-based)
  writeFileSync(join(bundle, "docker-compose.bundle.yml"), COMPOSE_BUNDLE, { mode: 0o644 });
  log(`bundled compose → ${join(bundle, "docker-compose.bundle.yml")}`);

  // Launcher wrapper
  const launchPath = join(scriptsDir, "launch.sh");
  writeFileSync(launchPath, LAUNCH_SH, { mode: 0o755 });
  log(`bundled launcher → ${launchPath}`);

  // README so the bundle is self-documenting when a user inspects it
  writeFileSync(join(bundle, "README.txt"), README, { mode: 0o644 });
}

main().catch((err: unknown) => {
  const msg = err instanceof Error ? err.message : String(err);
  process.stderr.write(`[postbundle] ${msg}\n`);
  process.exit(1);
});
