import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchDashboardSummary } from "./system";

const summary = () => ({
  projectCount: 1,
  totalItemCount: 2,
  perProject: {
    alpha: {
      totalCount: 2,
      completedCount: 1,
      statusCounts: { closed: 1 },
      typeCounts: { problem: 2 },
    },
  },
  statusDistribution: { closed: 1 },
  typeDistribution: { problem: 2 },
});

const respond = (body: unknown) =>
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(body)));
afterEach(() => vi.unstubAllGlobals());

describe("dashboard summary response", () => {
  it("preserves valid complete and empty structures", async () => {
    respond(summary());
    await expect(fetchDashboardSummary()).resolves.toEqual(summary());
    const empty = {
      projectCount: 0,
      totalItemCount: 0,
      perProject: {},
      statusDistribution: {},
      typeDistribution: {},
    };
    respond(empty);
    await expect(fetchDashboardSummary()).resolves.toEqual(empty);
  });

  it.each([
    { ...summary(), perProject: { alpha: null } },
    { ...summary(), perProject: { alpha: { totalCount: 2, completedCount: 1 } } },
    {
      ...summary(),
      perProject: { alpha: { ...summary().perProject.alpha, statusCounts: { closed: "1" } } },
    },
    { ...summary(), perProject: { alpha: { ...summary().perProject.alpha, typeCounts: [] } } },
    { ...summary(), statusDistribution: { closed: -1 } },
    { ...summary(), typeDistribution: { problem: 0.5 } },
    { ...summary(), projectCount: -1 },
    { ...summary(), totalItemCount: Number.MAX_SAFE_INTEGER + 1 },
  ])("rejects malformed nested counts instead of rendering success", async (payload) => {
    respond(payload);
    await expect(fetchDashboardSummary()).rejects.toMatchObject({
      status: 502,
      data: { error: "invalid_response" },
    });
  });
});
