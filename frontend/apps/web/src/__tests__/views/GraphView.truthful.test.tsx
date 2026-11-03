import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@tanstack/react-router", () => ({
  useParams: () => ({ projectId: "p1" }),
}));
vi.mock("@/api/client", () => ({
  client: { getAuthHeaders: () => ({}), getBackendURL: () => "" },
}));
vi.mock("@/components/graph/UnifiedGraphView", () => ({
  UnifiedGraphView: () => <div data-testid="graph-preview">Graph preview</div>,
}));

import { GraphView } from "@/pages/projects/views/GraphView";
import { useAuthStore } from "@/stores/authStore";

function mount() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <GraphView />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  useAuthStore.getState().setToken("first");
});
afterEach(() => {
  cleanup();
  useAuthStore.getState().setToken(null);
  vi.unstubAllGlobals();
});

describe("Project graph availability", () => {
  it("treats an unavailable relationship service as an error rather than an empty graph", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) =>
        url.includes("/links")
          ? { ok: false, status: 501 }
          : { ok: true, json: async () => ({ items: [], total: 0 }) },
      ),
    );
    mount();
    expect(await screen.findByRole("alert")).toHaveTextContent("Graph data is unavailable");
    expect(screen.queryByTestId("graph-preview")).not.toBeInTheDocument();
  });

  it("labels a bounded result partial and discloses unavailable navigation", async () => {
    const fetchMock = vi.fn(async (url: string) =>
      url.includes("/links")
        ? { ok: true, json: async () => ({ links: [], total: 0 }) }
        : { ok: true, json: async () => ({ items: [{ id: "i1", projectId: "p1" }], total: 2 }) },
    );
    vi.stubGlobal("fetch", fetchMock);
    mount();
    expect(await screen.findByRole("status")).toHaveTextContent("showing 1 of 2 items");
    const itemRequest = fetchMock.mock.calls
      .map(([url]) => url)
      .find((url) => url.includes("/items"));
    expect(itemRequest).toContain("limit=100");
    expect(itemRequest).toContain("offset=0");
    expect(itemRequest).not.toContain("skip=");
    expect(screen.getByText("Graph preview: item navigation is unavailable.")).toBeInTheDocument();
  });

  it("rejects malformed envelopes instead of treating them as empty", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => ({
        ok: true,
        json: async () => (url.includes("/links") ? { links: [] } : { items: [], total: 0 }),
      })),
    );
    mount();
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Graph data is unavailable"),
    );
  });

  it.each([
    { items: [], total: 51 },
    { items: [{ id: "i1", projectId: "other" }], total: 1 },
    {
      items: [
        { id: "i1", projectId: "p1" },
        { id: "i1", projectId: "p1" },
      ],
      total: 2,
    },
  ])("rejects invalid or cross-project item pages", async (body) => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => ({
        ok: true,
        json: async () => (url.includes("/links") ? { links: [], total: 0 } : body),
      })),
    );
    mount();
    expect(await screen.findByRole("alert")).toHaveTextContent("Graph data is unavailable");
    expect(screen.queryByTestId("graph-preview")).not.toBeInTheDocument();
  });

  it("rejects links with missing endpoints", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => ({
        ok: true,
        json: async () =>
          url.includes("/links")
            ? {
                links: [
                  { id: "l1", projectId: "p1", sourceId: "", targetId: "i1", type: "depends" },
                ],
                total: 1,
              }
            : { items: [{ id: "i1", projectId: "p1" }], total: 1 },
      })),
    );
    mount();
    expect(await screen.findByRole("alert")).toHaveTextContent("Graph data is unavailable");
  });

  it("does not reuse the previous user's graph when the auth session changes", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) =>
        useAuthStore.getState().token === "second"
          ? { ok: false, status: 403 }
          : {
              ok: true,
              json: async () =>
                url.includes("/links")
                  ? { links: [], total: 0 }
                  : { items: [{ id: "i1", projectId: "p1" }], total: 1 },
            },
      ),
    );
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <GraphView />
      </QueryClientProvider>,
    );
    await screen.findByTestId("graph-preview");
    act(() => {
      useAuthStore.getState().setToken("second");
    });
    expect(screen.queryByTestId("graph-preview")).not.toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("Graph data is unavailable");
  });

  it("hides cached graph data when the real auth store logs out", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (url.includes("/auth/logout")) return { ok: true, json: async () => ({}) };
        if (!useAuthStore.getState().token) return { ok: false, status: 401 };
        return {
          ok: true,
          json: async () =>
            url.includes("/links")
              ? { links: [], total: 0 }
              : { items: [{ id: "i1", projectId: "p1" }], total: 1 },
        };
      }),
    );
    mount();
    await screen.findByTestId("graph-preview");
    await act(async () => {
      await useAuthStore.getState().logout();
    });
    expect(screen.queryByTestId("graph-preview")).not.toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("Graph data is unavailable");
  });
});
