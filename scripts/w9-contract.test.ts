import { describe, expect, test } from "bun:test";
import { readFileSync, readdirSync } from "node:fs";
import { honestFallback, unavailableRouteTemplate } from "../api/honest-fallback";

const decisions = readFileSync("docs/operations/w9-route-decisions.csv", "utf8")
  .trim().split(/\r?\n/).slice(1).map((line) => line.split(","));

describe("W9 unavailable gateway contract", () => {
  test.each(decisions)("%s", (template, _family, _decision, _before, _after, _pr, methods) => {
    for (const method of methods === "ANY" ? ["GET", "POST", "PUT", "PATCH", "DELETE"] : [methods]) {
      let status = 0;
      let body: unknown;
      const res = {
        setHeader() {},
        status(code: number) { status = code; return res; },
        json(value: unknown) { body = value; },
      };
      honestFallback({ method, url: template.replace(/\{[^}]+\}/g, "private-id") + "?token=private-query" } as any, res as any);
      expect(status).toBe(501);
      expect(body).toEqual({ error: "not_implemented", route: template });
    }
  });
  test("inventory includes every required family", () => {
    const families = new Set(decisions.map((row) => row[1]));
    for (const family of ["integrations", "test-runs", "test-cases", "test-suites", "problems", "processes", "qa", "webhooks", "notifications"]) {
      expect(families.has(family)).toBe(true);
    }
    expect(decisions.length).toBeGreaterThan(200);
  });
  test("inventory matches the registered family modules without duplicates", () => {
    const root = "crates/tracera-server/src/routes/";
    const registered: string[] = [];
    for (const file of readdirSync(root).filter((file) => file.endsWith(".rs"))) {
      const source = readFileSync(root + file, "utf8");
      const declaration = source.match(/const (?:W9_)?ROUTES: &\[&str\] = &\[([\s\S]*?)\];/);
      if (!declaration) continue;
      registered.push(...[...declaration[1].matchAll(/"([^"]+)"/g)].map((match) => match[1]));
    }
    expect(new Set(registered).size).toBe(registered.length);
    expect(registered.sort()).toEqual(decisions.filter((row) => row[6] === "ANY").map((row) => row[0]).sort());
    for (const family of new Set(decisions.filter((row) => row[6] === "ANY").map((row) => row[1]))) {
      expect(readdirSync(root)).toContain(family.replaceAll("-", "_") + ".rs");
    }
  });
  test("unknown gateway paths never echo concrete identifiers", () => {
    expect(unavailableRouteTemplate("/api/v1/unknown-family/private-id")).toBe("/api/{*path}");
  });
});
