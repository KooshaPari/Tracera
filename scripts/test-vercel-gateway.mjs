import assert from "node:assert/strict";
import { test } from "node:test";

let serial = 0;
async function invoke({ backend = "", url = "/api/v1/health", method = "GET", headers = {}, body, fetcher }) {
  process.env.TRACERA_BACKEND_URL = backend;
  const previous = globalThis.fetch;
  globalThis.fetch = fetcher ?? (() => { throw new Error("unexpected fetch"); });
  const { default: route } = await import(`../api/[...path].ts?case=${serial++}`);
  const response = { headers: {}, code: undefined, body: undefined,
    setHeader(name, value) { this.headers[name.toLowerCase()] = value; return this; },
    status(code) { this.code = code; return this; },
    json(body) { this.body = body; return this; },
    send(body) { this.body = body; return this; },
    end() { return this; },
  };
  try { await route({ url, method, headers, body, query: {} }, response); }
  finally { globalThis.fetch = previous; }
  return response;
}

test("missing backend cannot synthesize health, readiness, or empty project data", async () => {
  for (const url of ["/api/healthz", "/api/ready", "/api/readyz", "/api/v1/health",
    "/api/v1/search/health", "/api/v1/projects", "/api/v1/items?project_id=p",
    "/api/v1/links?project_id=p", "/api/v1/dashboard/summary"]) {
    const res = await invoke({ url });
    assert.equal(res.code, 503, url);
    assert.deepEqual(res.body, { status: "unavailable", reason: "backend_not_configured" });
    assert.equal(res.headers["cache-control"], "no-store");
    assert.equal(res.headers["x-tracera-gateway-mode"], "unavailable");
  }
});

test("configured network failure cannot fall back to healthy or empty stubs", async () => {
  for (const url of ["/api/v1/health", "/api/v1/projects", "/api/v1/projects/p/import"]) {
    const res = await invoke({ backend: "https://example.invalid/api", url,
      fetcher: async () => { throw new TypeError("network failed"); } });
    assert.equal(res.code, 503);
    assert.equal(res.body.reason, "backend_unreachable");
  }
});

test("timeout reports unavailable and aborts upstream", async () => {
  const originalTimer = globalThis.setTimeout;
  globalThis.setTimeout = (callback) => originalTimer(callback, 0);
  try {
    const res = await invoke({ backend: "https://example.invalid/api",
      fetcher: (_url, { signal }) => new Promise((_resolve, reject) =>
        signal.addEventListener("abort", () => reject(new Error("aborted")), { once: true })) });
    assert.equal(res.code, 503);
    assert.equal(res.body.reason, "backend_timeout");
  } finally { globalThis.setTimeout = originalTimer; }
});

test("upstream 200, authorization failure, and 5xx retain body and status", async () => {
  for (const status of [200, 401, 403, 503]) {
    const res = await invoke({ backend: "https://example.invalid/api",
      fetcher: async () => new Response(JSON.stringify({ status: status === 200 ? "ok" : "upstream", service: "tracera-server", actual: status }),
        { status, headers: { "content-type": "application/json" } }) });
    assert.equal(res.code, status);
    assert.deepEqual(JSON.parse(res.body.toString()), { status: status === 200 ? "ok" : "upstream", service: "tracera-server", actual: status });
    assert.equal(res.headers["x-tracera-gateway-mode"], "proxy");
  }
});

test("failed response stream returns 503 before status or data is sent", async () => {
  const res = await invoke({ backend: "https://example.invalid/api",
    fetcher: async () => ({ status: 200, arrayBuffer: async () => { throw new Error("broken stream"); } }) });
  assert.equal(res.code, 503);
  assert.equal(res.body.reason, "backend_unreachable");
});

test("proxy preserves query, mutation body and workspace/CSRF browser headers", async () => {
  let forwarded;
  const headers = { "content-type": "application/json", origin: "https://app.invalid",
    referer: "https://app.invalid/project", cookie: "session=x", authorization: "Bearer x",
    "x-csrf-token": "token", "x-tracera-workspace": "workspace-b" };
  const res = await invoke({ backend: "https://example.invalid/api/",
    url: "/api/v1/projects/p/import?replace=true", method: "POST", headers,
    body: { nodes: [{ id: "a" }] },
    fetcher: async (url, init) => { forwarded = { url, init }; return new Response('{"imported":1}', { status: 201 }); } });
  assert.equal(res.code, 201);
  assert.equal(forwarded.url, "https://example.invalid/api/v1/projects/p/import?replace=true");
  assert.equal(forwarded.init.method, "POST");
  assert.equal(forwarded.init.redirect, "manual");
  for (const [key, value] of Object.entries(headers)) assert.equal(forwarded.init.headers[key], value);
  assert.deepEqual(JSON.parse(Buffer.from(forwarded.init.body).toString()), { nodes: [{ id: "a" }] });
});

test("CORS preflight remains available without claiming backend health", async () => {
  const res = await invoke({ method: "OPTIONS" });
  assert.equal(res.code, 204);
  assert.equal(res.headers["access-control-allow-origin"], "*");
  assert.equal(res.headers["x-tracera-gateway-mode"], undefined);
});

test("Access login HTML and malformed or wrong JSON cannot claim readiness", async () => {
  for (const [body, type] of [["<html>cloudflareaccess login</html>", "text/html"],
    ['{"status":"ready"}', "application/json"], ['{"status":"ok"}', "text/html"],
    ['broken', "application/json"]]) {
    const res = await invoke({ backend: "https://example.invalid/api",
      fetcher: async () => new Response(body, { headers: { "content-type": type } }) });
    assert.equal(res.code, 503);
    assert.equal(res.body.reason, "backend_health_invalid");
  }
  const ready = await invoke({ backend: "https://example.invalid/api", url: "/api/ready",
    fetcher: async () => new Response('{"status":"ready","service":"tracera-server","backend":"sqlite","version":"0.1.0","uptime_seconds":2}', { headers: { "content-type": "application/json" } }) });
  assert.equal(ready.code, 200);
});

