// Cloudflare secrets bootstrap helper
// Run with:   node scripts/wrangler-secrets-bootstrap.mjs
//
// Reads the names of all required secrets from the wrangler config,
// then `wrangler secret put $NAME` for each, prompting the operator.
// Stores nothing — values come from the operator at the terminal.

import { execSync } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";

const REQUIRED = [
  "TRACE_API_KEY",
  "CIVIS_PROVIDER_TOKEN",
  "PHENOTYPE_REGISTRY_TOKEN",
  "GITHUB_PAT",
];

const OPTIONAL = ["SENTRY_DSN", "OTEL_EXPORTER_OTLP_ENDPOINT"];

function list() {
  console.log("\nRequired secrets (must be set before deploy):");
  for (const s of REQUIRED) console.log("  - " + s);
  console.log("\nOptional secrets:");
  for (const s of OPTIONAL) console.log("  - " + s);
}

function checkWrangler() {
  try {
    execSync("npx wrangler --version", { stdio: "pipe" });
  } catch (e) {
    console.error("wrangler not installed. Run: npm i -g wrangler");
    process.exit(1);
  }
}

function pushSecret(name) {
  console.log("\nSetting secret: " + name + " (value will be prompted)");
  try {
    execSync("npx wrangler secret put " + name, { stdio: "inherit" });
    return true;
  } catch (e) {
    console.error("Failed to set " + name + ": " + e.message);
    return false;
  }
}

function dryRun() {
  console.log("Dry run — listing required secrets and target environment.");
  list();
}

function main() {
  const args = process.argv.slice(2);
  if (args.includes("--dry-run") || args.includes("-n")) return dryRun();
  if (args.includes("--list") || args.includes("-l")) return list();

  checkWrangler();
  list();
  console.log("\nProceeding to set REQUIRED secrets. Press <Ctrl+C> to abort.\n");
  const ok = [];
  const fail = [];
  for (const name of REQUIRED) {
    if (pushSecret(name)) ok.push(name); else fail.push(name);
  }
  console.log("\nDone.");
  console.log("  Set:    " + ok.join(", "));
  if (fail.length) console.log("  Failed: " + fail.join(", "));
}

main();
