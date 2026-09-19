import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { runFrontendPreflight } from "./preflight";

const RUST_READY_RESPONSE = {
  backend: "sqlite",
  service: "tracera-server",
  status: "ready",
  uptime_seconds: 1,
  version: "0.1.3-test",
};

describe("frontend preflight", () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="root"></div>';
    Object.defineProperty(HTMLElement.prototype, "animate", {
      configurable: true,
      value: vi.fn(),
    });
    Object.defineProperty(HTMLElement.prototype, "scrollTo", {
      configurable: true,
      value: vi.fn(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders only the dependencies advertised by the Rust readiness contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        () =>
          new Response(JSON.stringify(RUST_READY_RESPONSE), {
            headers: { "content-type": "application/json" },
            status: 200,
          }),
      ),
    );

    await expect(runFrontendPreflight()).resolves.toEqual({ errors: [], ok: true });

    expect(document.querySelectorAll("[data-infra]")).toHaveLength(1);
    expect(document.querySelector('[data-infra="database"]')).not.toBeNull();
    expect(document.querySelector("[data-infra-list]")).not.toHaveTextContent("Checking");
  });

  it("falls back to the next health path after a non-ok response", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(null, { status: 404 }))
      .mockResolvedValueOnce(new Response(null, { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(runFrontendPreflight()).resolves.toEqual({ errors: [], ok: true });

    // Assert the probe order, not the resolved origin: the base host comes from
    // window.location, which differs between a local run and CI.
    expect(fetchMock.mock.calls.slice(0, 2).map(([url]) => new URL(String(url)).pathname)).toEqual([
      "/ready",
      "/health",
    ]);
  });

  it("uses a failure color with WCAG AA contrast against the preflight card", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => {
        throw new Error("offline");
      }),
    );

    await runFrontendPreflight();

    const status = document.querySelector<HTMLElement>("[data-status-text]");
    if (!status) {
      throw new Error("Expected a preflight status element");
    }
    expect(status).toHaveTextContent("Down");
    expect(contrastRatio(status.style.color, "#211b23")).toBeGreaterThanOrEqual(4.5);
  });

  it("reports the final probe path for a CORS or network TypeError", async () => {
    const fetchMock = vi.fn(() => Promise.reject(new TypeError("Failed to fetch")));
    vi.stubGlobal("fetch", fetchMock);

    const result = await runFrontendPreflight();

    expect(result.ok).toBe(false);
    expect(result.errors[0]).toContain("Health check failed for /api/v1/health");
    expect(document.querySelector("[data-hint]")).toHaveTextContent("CORS or network error");
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("reports a timeout with the final probe path", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new DOMException("The operation timed out", "AbortError"))),
    );

    const result = await runFrontendPreflight();

    expect(result.errors[0]).toContain("Health check failed for /api/v1/health");
    expect(document.querySelector("[data-hint]")).toHaveTextContent("timed out");
  });

  it("reports the HTTP status and final probe path for non-ok responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(null, { status: 404 }))),
    );

    const result = await runFrontendPreflight();

    expect(result.errors[0]).toContain("Health check failed for /api/v1/health (HTTP 404)");
    expect(document.querySelector("[data-hint]")).toHaveTextContent("returned HTTP 404");
  });

  it.each([401, 403])("keeps the guarded-route early return for HTTP %i", async (status) => {
    const fetchMock = vi.fn(() => Promise.resolve(new Response(null, { status })));
    vi.stubGlobal("fetch", fetchMock);

    const result = await runFrontendPreflight();

    expect(result.errors[0]).toContain(`Health check failed for /ready (HTTP ${status})`);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(document.querySelector("[data-hint]")).toHaveTextContent("guarded by auth");
  });

  it("stops probing once the shared budget is exhausted", async () => {
    // Without a shared budget a host that never answers costs one timeout per
    // path. Simulate the clock jumping past the budget after the first probe and
    // assert the fallbacks are skipped instead of each paying the full timeout.
    const fetchMock = vi.fn(() =>
      Promise.reject(new DOMException("The operation timed out", "AbortError")),
    );
    vi.stubGlobal("fetch", fetchMock);
    // Date.now is read once to arm the deadline and once per loop iteration, so
    // two reads at t=0 admit the first probe and the jump past 10s ends the loop.
    const nowSpy = vi
      .spyOn(Date, "now")
      .mockReturnValueOnce(0)
      .mockReturnValueOnce(0)
      .mockReturnValue(30_000);

    try {
      const result = await runFrontendPreflight();

      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(result.ok).toBe(false);
    } finally {
      nowSpy.mockRestore();
    }
  });
});

function contrastRatio(foreground: string, background: string): number {
  const toLinear = (component: number): number => {
    const normalized = component / 255;
    return normalized <= 0.039_28 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
  };
  const luminance = (value: string): number => {
    const channels = value.startsWith("#")
      ? [0, 2, 4].map((offset) => Number.parseInt(value.slice(offset + 1, offset + 3), 16))
      : (value.match(/\d+/g) ?? []).slice(0, 3).map(Number);
    const [red, green, blue] = channels;
    return 0.2126 * toLinear(red) + 0.7152 * toLinear(green) + 0.0722 * toLinear(blue);
  };
  const first = luminance(foreground);
  const second = luminance(background);
  const [lighter, darker] = first >= second ? [first, second] : [second, first];
  return (lighter + 0.05) / (darker + 0.05);
}
