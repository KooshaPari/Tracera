#!/usr/bin/env node
/**
 * Merge Go and Python OpenAPI specs into a single gateway contract.
 * External clients (frontend, MCP, CLI) should use this spec with baseUrl = gateway URL.
 * Usage: node scripts/merge-gateway-openapi.js [gatewayUrl]
 * Default gatewayUrl: http://localhost:4000
 */

const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const openapiDir = path.join(projectRoot, "openapi");
const goSpecPath = path.join(openapiDir, "go-api.json");
const pythonSpecPath = path.join(openapiDir, "python-api.json");
const outPath = path.join(openapiDir, "gateway-api.json");

const gatewayUrl = process.argv[2] || "http://localhost:4000";

function loadSpec(p) {
  if (!fs.existsSync(p)) {
    console.warn(`Warning: ${p} not found (run generate:openapi first)`);
    return null;
  }
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function mergePaths(goSpec, pythonSpec) {
  const paths = {};
  for (const spec of [goSpec, pythonSpec]) {
    if (!spec?.paths) continue;
    for (const [pathKey, pathItem] of Object.entries(spec.paths)) {
      if (!paths[pathKey]) paths[pathKey] = {};
      for (const [method, op] of Object.entries(pathItem)) {
        if (["get", "post", "put", "patch", "delete", "options", "head"].includes(method.toLowerCase())) {
          paths[pathKey][method] = op;
        }
      }
    }
  }
  return paths;
}

function main() {
  const goSpec = loadSpec(goSpecPath);
  const pythonSpec = loadSpec(pythonSpecPath);
  if (!goSpec && !pythonSpec) {
    console.error("No OpenAPI specs found. Run: bun run generate:openapi");
    process.exit(1);
  }

  const base = goSpec || pythonSpec;
  const merged = {
    openapi: base.openapi || "3.0.3",
    info: {
      ...base.info,
      title: base.info?.title ? `${base.info.title} (Gateway)` : "TraceRTM API (Gateway)",
      description: [
        base.info?.description || "",
        "Merged gateway contract. All external clients must use the gateway URL as baseUrl.",
      ]
        .filter(Boolean)
        .join("\n\n"),
    },
    servers: [{ url: gatewayUrl.replace(/\/$/, ""), description: "Gateway (Caddy)" }],
    paths: mergePaths(goSpec || {}, pythonSpec || {}),
    components: {
      schemas: { ...goSpec?.components?.schemas, ...pythonSpec?.components?.schemas },
      securitySchemes: {
        ...goSpec?.components?.securitySchemes,
        ...pythonSpec?.components?.securitySchemes,
      },
    },
    security: base.security || [],
    tags: [
      ...(goSpec?.tags || []),
      ...(pythonSpec?.tags || []).filter((t) => !(goSpec?.tags || []).some((g) => g.name === t.name)),
    ],
  };

  fs.mkdirSync(openapiDir, { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(merged, null, 2), "utf8");
  console.log(`Wrote ${outPath} (server: ${gatewayUrl})`);
}

main();
