import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useItems } from "@/hooks/useItems";

vi.mock("@/stores/authStore", () => ({
  useAuthStore: (selector: (state: { token: undefined }) => unknown) =>
    selector({ token: undefined }),
}));

function wrapper({ children }: { children: ReactNode }): JSX.Element {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("canonical items list contract", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    globalThis.fetch = vi.fn();
  });

  it("requests only query parameters the Rust handler accepts", async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0 })));
    const { result } = renderHook(() => useItems({ projectId: "p1", limit: 10, offset: 10 }), {
      wrapper,
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    const url = String(vi.mocked(fetch).mock.calls[0]?.[0]);
    const params = new URL(url, "http://localhost").searchParams;
    expect([...params.keys()].sort()).toEqual(["limit", "offset", "project_id"]);
    expect(params.get("project_id")).toBe("p1");
    expect(params.get("offset")).toBe("10");
  });

  it("fails a parent-filtered request instead of returning unfiltered results", async () => {
    const { result } = renderHook(() => useItems({ parentId: "parent-1" }), { wrapper });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(String(result.current.error)).toMatch(/parent.*not supported/i);
    expect(fetch).not.toHaveBeenCalled();
  });

  it("rejects records from another project", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(
        JSON.stringify({
          items: [
            {
              id: "i1",
              projectId: "other",
              view: "features",
              title: "Other",
              type: "feature",
              status: "todo",
              priority: "medium",
              version: 1,
              createdAt: "2026-01-01T00:00:00Z",
              updatedAt: "2026-01-01T00:00:00Z",
            },
          ],
          total: 1,
        }),
      ),
    );
    const { result } = renderHook(() => useItems({ projectId: "p1" }), { wrapper });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(String(result.current.error)).toMatch(/another project/i);
  });

  it("rejects duplicate item IDs in the same page", async () => {
    const item = {
      id: "i1",
      projectId: "p1",
      view: "feature",
      title: "Item",
      type: "feature",
      status: "todo",
      priority: "medium",
      version: 1,
      createdAt: "2026-01-01T00:00:00Z",
      updatedAt: "2026-01-01T00:00:00Z",
    };
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ items: [item, item], total: 2 })),
    );
    const { result } = renderHook(() => useItems({ projectId: "p1" }), { wrapper });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(String(result.current.error)).toMatch(/duplicate/i);
  });

  it.each([
    null,
    {},
    { items: [] },
    { items: [], total: 51 },
    { items: [null], total: 1 },
    { items: [], total: -1 },
    { items: [{ id: "a" }], total: 0 },
  ])("rejects malformed response %# rather than reporting an empty list", async (payload) => {
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify(payload)));
    const { result } = renderHook(() => useItems(), { wrapper });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
  });
});
