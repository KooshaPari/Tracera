import { describe, expect, it } from "vitest";
import { aggregateDashboardCounts, projectStatsFor } from "./dashboard-summary";
import type { DashboardProjectStats } from "@/api/system";

const stats = (
  statusCounts: Record<string, number>,
  typeCounts: Record<string, number>,
): DashboardProjectStats => ({ totalCount: 2, completedCount: 0, statusCounts, typeCounts });

describe("dashboard count aggregation", () => {
  it("treats prototype property names as ordinary keys", () => {
    const hostile = JSON.parse('{"__proto__":2,"constructor":3,"toString":4}') as Record<
      string,
      number
    >;
    const projects = { a: stats(hostile, hostile), b: stats(hostile, hostile) };
    const expected = [
      { name: "__proto__", value: 4 },
      { name: "constructor", value: 6 },
      { name: "toString", value: 8 },
    ];
    expect(aggregateDashboardCounts(projects, "statusCounts")).toEqual(expected);
    expect(aggregateDashboardCounts(projects, "typeCounts")).toEqual(expected);
    expect(Object.getPrototypeOf({})).toBe(Object.prototype);
  });
  it("does not invent project stats from inherited properties", () => {
    expect(projectStatsFor({}, "constructor")).toBeUndefined();
    expect(projectStatsFor({}, "__proto__")).toBeUndefined();
    const projects = JSON.parse(
      '{"__proto__":{"totalCount":2,"completedCount":0,"statusCounts":{},"typeCounts":{}}}',
    ) as Record<string, DashboardProjectStats>;
    expect(projectStatsFor(projects, "__proto__")?.totalCount).toBe(2);
  });
});
