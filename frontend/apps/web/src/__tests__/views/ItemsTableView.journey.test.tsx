import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ItemsTableView } from "@/views/ItemsTableView";

vi.mock("@tanstack/react-router", () => ({ useNavigate: () => vi.fn(), useSearch: () => ({}) }));
vi.mock("@/stores/authStore", () => ({
  useAuthStore: (selector: (state: { token: undefined }) => unknown) =>
    selector({ token: undefined }),
}));
vi.mock("@/hooks/useProjects", () => ({ useProjects: () => ({ data: [] }) }));
vi.mock("@/views/items-table/ItemsTableFiltersBar", () => ({
  ItemsTableFiltersBar: ({ onRefresh }: { onRefresh: () => void }) => (
    <button onClick={onRefresh}>Refresh</button>
  ),
}));
vi.mock("@/views/items-table/ItemsTableContent", () => ({
  ItemsTableContent: ({ filteredItems }: { filteredItems: { id: string; title: string }[] }) => (
    <div>
      {filteredItems.length === 0
        ? "No items"
        : filteredItems.map((item) => <div key={item.id}>{item.title}</div>)}
    </div>
  ),
}));

const allItems = Array.from({ length: 51 }, (_, index) => ({
  id: `item-${index + 1}`,
  projectId: "p1",
  view: "feature",
  type: "feature",
  title: `Item ${index + 1}`,
  status: "todo",
  priority: "medium",
  version: 1,
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
}));

function renderList() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <ItemsTableView projectId="p1" />
    </QueryClientProvider>,
  );
}

describe("items list journey against a strict API fixture", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn(async (input) => {
      const params = new URL(String(input), "http://localhost").searchParams;
      if (
        [...params.keys()].some(
          (key) => !["project_id", "view", "status", "limit", "offset"].includes(key),
        )
      ) {
        return new Response("unknown parameter", { status: 400 });
      }
      const offset = Number(params.get("offset") ?? 0);
      const limit = Number(params.get("limit") ?? 50);
      return new Response(
        JSON.stringify({
          items: allItems.slice(offset, offset + limit),
          total: allItems.length,
          offset,
          limit,
        }),
      );
    }) as typeof fetch;
  });

  it("reads, navigates to the next page, and returns to the previous page", async () => {
    renderList();
    expect(await screen.findByText("Item 1")).toBeInTheDocument();
    expect(screen.queryByText("Item 51")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Next page" }));
    expect(await screen.findByText("Item 51")).toBeInTheDocument();
    expect(screen.queryByText("Item 1")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Previous page" }));
    expect(await screen.findByText("Item 1")).toBeInTheDocument();
    const offsets = vi
      .mocked(fetch)
      .mock.calls.map(([url]) =>
        new URL(String(url), "http://localhost").searchParams.get("offset"),
      );
    expect(offsets).toEqual(expect.arrayContaining(["0", "50"]));
  });

  it("retains the last page but warns when refresh fails", async () => {
    renderList();
    expect(await screen.findByText("Item 1")).toBeInTheDocument();
    vi.mocked(fetch).mockResolvedValueOnce(new Response("unavailable", { status: 503 }));
    fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/stale/i));
    expect(screen.getByText("Item 1")).toBeInTheDocument();
  });

  it("hides cached records if access is revoked during refresh", async () => {
    renderList();
    expect(await screen.findByText("Item 1")).toBeInTheDocument();
    vi.mocked(fetch).mockResolvedValueOnce(new Response("forbidden", { status: 403 }));
    fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/access.*denied/i));
    expect(screen.queryByText("Item 1")).not.toBeInTheDocument();
    expect(screen.queryByText(/51 total items/i)).not.toBeInTheDocument();
  });

  it("withholds rows and totals when the API returns an unsupported status or view", async () => {
    const unsupportedItem = { ...allItems[0], view: "unmapped-view", status: "unmapped-status" };
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ items: [unsupportedItem], total: 1 })),
    );
    renderList();
    expect(await screen.findByRole("alert")).toHaveTextContent(/does not support.*view.*status/i);
    expect(screen.queryByText("Item 1")).not.toBeInTheDocument();
    expect(screen.queryByText(/total items/i)).not.toBeInTheDocument();
  });

  it("can advance past an unsupported page without displaying its data or total", async () => {
    const firstPage = allItems.slice(0, 50);
    firstPage[0] = { ...firstPage[0]!, status: "unmapped-status" };
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ items: firstPage, total: 51 })),
    );
    renderList();
    expect(await screen.findByRole("alert")).toHaveTextContent(/status/i);
    expect(screen.queryByText("Item 1")).not.toBeInTheDocument();
    expect(screen.queryByText(/total items/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Next page" }));
    expect(await screen.findByText("Item 51")).toBeInTheDocument();
  });
});
