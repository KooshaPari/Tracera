/**
 * Tests for System API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchSystemStatus } from "@/api/system";

const mocks = vi.hoisted(() => ({ get: vi.fn() }));

vi.mock("@/api/client", () => ({
  client: {
    API_BASE_URL: "",
    apiClient: { GET: mocks.get },
    getAuthHeaders: () => ({}),
  },
}));

const reply = (status: number, data?: unknown) => ({
  response: new Response(null, { status }),
  data,
  error: status >= 400 ? { error: "failed" } : undefined,
});

beforeEach(() => {
  vi.clearAllMocks();
});

describe(fetchSystemStatus, () => {
  it("reports real backend health when the payload carries status and uptime", async () => {
    mocks.get.mockResolvedValue(reply(200, { status: "ok", uptime_seconds: 12 }));

    expect(await fetchSystemStatus()).toMatchObject({
      status: "healthy",
      uptime: 12,
      queuedJobs: undefined,
    });
  });

  it("preserves a degraded backend as degraded", async () => {
    mocks.get.mockResolvedValue(reply(200, { status: "degraded", uptime_seconds: 3 }));

    expect(await fetchSystemStatus()).toMatchObject({ status: "degraded", uptime: 3 });
  });

  it.each([401, 403, 404, 429, 500, 502, 503])(
    "never reports healthy on HTTP %s",
    async (status) => {
      mocks.get.mockResolvedValue(reply(status));

      await expect(fetchSystemStatus()).rejects.toMatchObject({ status });
    },
  );

  it("propagates transport failure instead of inventing uptime", async () => {
    mocks.get.mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(fetchSystemStatus()).rejects.toThrow("Failed to fetch");
  });

  it.each([null, {}, "<html>sign in</html>", { status: "ok" }] as unknown[])(
    "rejects a 2xx payload that is not a health contract (%#)",
    async (payload) => {
      mocks.get.mockResolvedValue(reply(200, payload));

      await expect(fetchSystemStatus()).rejects.toMatchObject({ status: 502 });
    },
  );
});
