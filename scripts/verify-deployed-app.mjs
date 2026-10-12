import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

export function verifyDeployedApp(status, body) {
  if (!/^2\d\d$/.test(String(status))) {
    throw new Error("Deployment fetch did not return a successful HTTP status");
  }
  if (!body.trim()) throw new Error("Deployment returned an empty body");
  if (/vercel\.com\/login|sso-api/i.test(body)) {
    throw new Error("Deployment protection blocked verification; app contents remain unverified");
  }
  if (/scaffolding coming soon/i.test(body)) {
    throw new Error("Deployment serves the placeholder instead of the built app");
  }
  if (!/<[^>]+\bid\s*=\s*["']root["'][^>]*>/i.test(body)) {
    throw new Error("Deployment has no SPA root");
  }
  if (!/<script\b(?=[^>]*\btype\s*=\s*["']module["'])(?=[^>]*\bsrc\s*=\s*["']\/assets\/[^"']+\.js["'])[^>]*>/i.test(body)) {
    throw new Error("Deployment has no built application module");
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [status, bodyPath] = process.argv.slice(2);
  verifyDeployedApp(status, readFileSync(bodyPath, "utf8"));
  console.log("PASS: deployment serves the built SPA; backend acceptance is a separate gate");
}
