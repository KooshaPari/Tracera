import assert from "node:assert/strict";
import { test } from "node:test";

let serial = 0;
async function invoke({ backend = "https://tracera.pheno.studio/api", id, secret, headers = {}, fetcher }) {
  const envNames = ["TRACERA_BACKEND_URL", "TRACERA_CF_ACCESS_CLIENT_ID", "TRACERA_CF_ACCESS_CLIENT_SECRET"];
  const previousEnv = Object.fromEntries(envNames.map(name => [name, process.env[name]]));
  const previousFetch = globalThis.fetch;
  for (const [name, value] of [[envNames[0], backend], [envNames[1], id], [envNames[2], secret]]) {
    if (value === undefined) delete process.env[name]; else process.env[name] = value;
  }
  globalThis.fetch = fetcher ?? (() => { throw new Error("unexpected fetch"); });
  const response = { headers: {}, code: undefined, body: undefined,
    setHeader(name, value) { this.headers[name.toLowerCase()] = value; return this; },
    status(code) { this.code = code; return this; }, json(body) { this.body = body; return this; },
    send(body) { this.body = body; return this; }, end() { return this; },
  };
  try {
    const { default: route } = await import(`../api/[...path].ts?accesscase=${serial++}`);
    await route({ url: "/api/v1/projects", method: "GET", headers, query: {} }, response);
    return response;
  } finally {
    globalThis.fetch = previousFetch;
    for (const [name, value] of Object.entries(previousEnv)) {
      if (value === undefined) delete process.env[name]; else process.env[name] = value;
    }
  }
}

test("valid server-only pair is sent to configured HTTPS origin while browser overrides are ignored", async () => {
  let upstream;
  const res = await invoke({ id: "server-id", secret: "server-secret",
    headers: { "cf-access-client-id": "browser-id", "cf-access-client-secret": "browser-secret",
               authorization: "Bearer rust-session", origin: "https://frontend.invalid" },
    fetcher: async (url, init) => { upstream = { url, init }; return new Response('{"projects":[]}',
      { headers: { "content-type": "application/json", "CF-Access-Client-Secret": "upstream-hidden" } }); } });
  assert.equal(upstream.url, "https://tracera.pheno.studio/api/v1/projects");
  assert.equal(upstream.init.headers["cf-access-client-id"], "server-id");
  assert.equal(upstream.init.headers["cf-access-client-secret"], "server-secret");
  assert.equal(upstream.init.headers.authorization, "Bearer rust-session");
  assert.equal(upstream.init.headers.origin, "https://frontend.invalid");
  assert.equal(upstream.init.redirect, "manual");
  assert.equal(res.code, 200);
  assert.equal(res.headers["cf-access-client-secret"], undefined);
  assert.equal(res.headers["cf-access-client-id"], undefined);
  assert(!JSON.stringify(res).includes("server-secret"));
});

test("partial or malformed credential pair fails before any upstream request", async () => {
  for (const [id, secret] of [["server-id", undefined], [undefined, "server-secret"],
                            ["server-id", " "], ["bad\nheader", "server-secret"]]) {
    let called = false;
    const res = await invoke({ id, secret, fetcher: async () => { called = true; throw new Error("unexpected"); } });
    assert.equal(called, false);
    assert.equal(res.code, 503);
    assert.equal(res.body.reason, "backend_access_configuration_invalid");
    assert.equal(res.headers["cache-control"], "no-store");
    assert(!JSON.stringify(res).includes("server-secret"));
  }
});

test("credential pair cannot be transmitted to HTTP, URL userinfo, query, or fragment targets", async () => {
  for (const backend of ["http://127.0.0.1:8080/api", "https://user:pass@origin.invalid/api",
                         "https://origin.invalid/api?credential=value", "https://origin.invalid/api#fragment", "invalid"]) {
    let called = false;
    const res = await invoke({ backend, id: "server-id", secret: "server-secret",
      fetcher: async () => { called = true; throw new Error("unexpected"); } });
    assert.equal(called, false);
    assert.equal(res.code, 503);
    assert.equal(res.body.reason, "backend_access_configuration_invalid");
  }
});

test("without server pair, incoming browser service-token headers are never forwarded", async () => {
  let upstream;
  const res = await invoke({ headers: { "cf-access-client-id": "browser-id", "cf-access-client-secret": "browser-secret" },
    fetcher: async (_url, init) => { upstream = init.headers; return new Response('{"error":"denied"}', { status: 403 }); } });
  assert.equal(upstream["cf-access-client-id"], undefined);
  assert.equal(upstream["cf-access-client-secret"], undefined);
  assert.equal(res.code, 403);
});

test("policy rejection is preserved and network errors cannot reveal credentials or log them", async () => {
  const originals = { log: console.log, warn: console.warn, error: console.error };
  const logs = [];
  for (const name of Object.keys(originals)) console[name] = (...args) => logs.push(args);
  try {
    const denied = await invoke({ id: "server-id", secret: "server-secret",
      fetcher: async () => new Response('{"error":"Access policy denied"}', { status: 403 }) });
    assert.equal(denied.code, 403);
    const failed = await invoke({ id: "server-id", secret: "server-secret",
      fetcher: async () => { throw new Error("server-id server-secret"); } });
    assert.equal(failed.code, 503);
    assert.equal(failed.body.reason, "backend_unreachable");
    assert(!JSON.stringify(failed).includes("server-secret"));
    assert.deepEqual(logs, []);
  } finally {
    Object.assign(console, originals);
  }
});
