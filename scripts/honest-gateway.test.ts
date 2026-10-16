import { describe, expect, test } from "bun:test";
import handler from "../api/[...path]";
import { readFileSync } from "node:fs";

function response() {
  const result = { statusCode: 0, body: undefined as any, headers: {} as Record<string, string> };
  const res = {
    setHeader(name: string, value: string) {
      result.headers[name.toLowerCase()] = value;
      return res;
    },
    status(code: number) {
      result.statusCode = code;
      return res;
    },
    json(body: unknown) {
      result.body = body;
      return res;
    },
    end() {
      return res;
    },
    send(body: unknown) {
      result.body = body;
      return res;
    },
  };
  return { result, res };
}
const registered = [
  ...readFileSync("crates/tracera-server/src/router.rs", "utf8").matchAll(/\.route\(\s*"([^"]+)"/g),
].map((m) => m[1].replace(/\{[^}]+\}/g, "probe-id"));

describe("Vercel honest gateway GET reprobe", () => {
  test.each([
    ...new Set([
      ...registered,
      "/api/v1/events",
      "/api/v1/reports",
      "/api/v1/projects/probe/matrix",
    ]),
  ])("%s", async (path) => {
    const { result, res } = response();
    await handler({ method: "GET", url: path, query: {}, headers: {} } as any, res as any);
    if (["/health", "/healthz"].includes(path)) {
      expect(result.statusCode).toBe(200);
      expect(result.body).toMatchObject({ source: "vercel-gateway", backend: "unavailable" });
    } else if (["/ready", "/readyz", "/api/v1/health"].includes(path)) {
      expect(result.statusCode).toBe(503);
    } else {
      expect(result.statusCode).toBe(501);
      expect(result.body).toEqual({ error: "not_implemented", route: path, since: "2026-10-16" });
      expect(result.headers["x-tracera-not-implemented"]).toBe("true");
    }
    expect(result.body?.stub).not.toBe(true);
    expect(result.headers["x-tracera-source"]).toBe("vercel-gateway");
  });
  test("preflight remains 204", async () => {
    const { result, res } = response();
    await handler(
      { method: "OPTIONS", url: "/api/v1/items", query: {}, headers: {} } as any,
      res as any,
    );
    expect(result.statusCode).toBe(204);
  });
});

test("real upstream item payload and source are preserved", async () => {
  const source = `
    globalThis.fetch = async () => Response.json({ items: [{ id: 'real-item' }], source: 'canonical-store' }, { headers: { 'x-tracera-source': 'canonical-store' } });
    const { default: handler } = await import('./api/[...path].ts');
    let status, body; const headers = {};
    const res = { setHeader(k,v) { headers[k]=v; return this; }, status(s) { status=s; return this; }, send(b) { body=JSON.parse(b.toString()); return this; } };
    await handler({ method:'GET',url:'/api/v1/items',query:{},headers:{} },res);
    if (status !== 200 || body.items[0].id !== 'real-item' || headers['x-tracera-source'] !== 'canonical-store') throw new Error('real data was changed');
    console.log('real upstream data and source preserved');
  `;
  const child = Bun.spawn([process.execPath, "-e", source], {
    cwd: process.cwd(),
    env: { ...process.env, TRACERA_BACKEND_URL: "https://backend.invalid/api" },
    stdout: "pipe",
    stderr: "pipe",
  });
  const output = await new Response(child.stdout).text();
  const error = await new Response(child.stderr).text();
  expect(await child.exited, error).toBe(0);
  expect(output).toContain("real upstream data and source preserved");
});
