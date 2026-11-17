import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, it, expect, vi, afterEach } from "vitest";
import { useDashboardSummary } from "./useDashboardSummary";
import { persistedProjectCount } from "@/lib/project-count";
vi.mock("@/stores/authStore", () => ({
  useAuthStore: (selector: (state: { token: null }) => unknown) => selector({ token: null }),
}));
vi.mock("../api/system", () => ({
  fetchDashboardSummary: vi.fn(async () => ({
    perProject: {
      alpha: {
        totalCount: 533,
        completedCount: 1,
        statusCounts: { open: 532, closed: 1 },
        typeCounts: {},
      },
    },
    projectCount: 1,
    totalItemCount: 533,
    statusDistribution: { open: 532, closed: 1 },
    typeDistribution: {},
  })),
}));
afterEach(() => vi.clearAllMocks());
describe("persisted project totals", () => {
  it("fetches dashboard summary for a cookie session without a bearer token", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(() => useDashboardSummary(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.totalItemCount).toBe(533);
    expect(result.current.data?.perProject.alpha?.totalCount).toBe(
      persistedProjectCount({ problem_count: 533 }),
    );
  });
  it("uses actual project counts and rejects missing or fabricated defaults", () => {
    expect(persistedProjectCount({ problem_count: 533 })).toBe(533);
    expect(persistedProjectCount({ problem_count: 0 })).toBe(0);
    for (const value of [{}, { problem_count: -1 }, { problem_count: "533" }, null]) {
      expect(() => persistedProjectCount(value)).toThrow("Project count unavailable");
    }
  });
});
