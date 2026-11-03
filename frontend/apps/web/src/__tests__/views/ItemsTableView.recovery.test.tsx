import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useItems } from "@/hooks/useItems";
import { ItemsTableView } from "@/views/ItemsTableView";

vi.mock("@tanstack/react-router", () => ({ useNavigate: () => vi.fn(), useSearch: () => ({}) }));
vi.mock("@/hooks/useProjects", () => ({ useProjects: () => ({ data: [] }) }));
vi.mock("@/hooks/useItems", () => ({
  useItems: vi.fn(),
  useCreateItem: () => ({ isPending: false, mutate: vi.fn() }),
  useDeleteItem: () => ({ mutate: vi.fn() }),
}));
vi.mock("@/views/items-table/ItemsTableFiltersBar", () => ({
  ItemsTableFiltersBar: ({ onRefresh }: { onRefresh: () => void }) => (
    <button onClick={onRefresh}>Refresh</button>
  ),
}));
vi.mock("@/views/items-table/ItemsTableContent", () => ({
  ItemsTableContent: ({
    filteredItems,
    liveMessageValue,
  }: {
    filteredItems: { title: string }[];
    liveMessageValue: string;
  }) => (
    <div>
      <span>{liveMessageValue}</span>
      {filteredItems.length === 0 ? "No items" : filteredItems.map((item) => item.title).join(", ")}
    </div>
  ),
}));

describe("items list recovery behavior", () => {
  const refetch = vi.fn();
  beforeEach(() => {
    vi.clearAllMocks();
    refetch.mockResolvedValue({ isError: false });
  });

  it("reports a failed initial request without saying the list is empty", () => {
    vi.mocked(useItems).mockReturnValue({
      isLoading: false,
      isError: true,
      data: undefined,
      refetch,
    } as never);
    render(<ItemsTableView projectId="p1" />);
    expect(screen.getByRole("alert")).toHaveTextContent(/could not load/i);
    expect(screen.queryByText("No items")).not.toBeInTheDocument();
  });

  it("says cached data is stale when a later request fails", () => {
    vi.mocked(useItems).mockReturnValue({
      isLoading: false,
      isError: true,
      data: { items: [], total: 0 },
      refetch,
    } as never);
    render(<ItemsTableView projectId="p1" />);
    expect(screen.getByRole("alert")).toHaveTextContent(/stale/i);
  });

  it("fetches on refresh and reports a failed refresh rather than success", async () => {
    refetch.mockResolvedValue({ isError: true });
    vi.mocked(useItems).mockReturnValue({
      isLoading: false,
      isError: false,
      data: { items: [], total: 0 },
      refetch,
    } as never);
    render(<ItemsTableView projectId="p1" />);
    fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
    expect(refetch).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(screen.getByText(/refresh failed/i)).toBeInTheDocument());
  });

  it("warns when client-side filtering covers only one page", () => {
    vi.mocked(useItems).mockReturnValue({
      isLoading: false,
      isError: false,
      data: { items: [], total: 51 },
      refetch,
    } as never);
    render(<ItemsTableView projectId="p1" />);
    expect(screen.getByText(/only.*loaded items/i)).toBeInTheDocument();
  });

  it("navigates server pages and returns to the first page when project changes", () => {
    vi.mocked(useItems).mockReturnValue({
      isLoading: false,
      isError: false,
      data: { items: [], total: 51 },
      refetch,
    } as never);
    const { rerender } = render(<ItemsTableView projectId="p1" />);
    fireEvent.click(screen.getByRole("button", { name: "Next page" }));
    expect(vi.mocked(useItems)).toHaveBeenLastCalledWith(
      expect.objectContaining({ projectId: "p1", offset: 50, limit: 50 }),
    );
    rerender(<ItemsTableView projectId="p2" />);
    expect(vi.mocked(useItems)).toHaveBeenLastCalledWith(
      expect.objectContaining({ projectId: "p2", offset: 0, limit: 50 }),
    );
    rerender(<ItemsTableView projectId="p1" />);
    expect(vi.mocked(useItems)).toHaveBeenLastCalledWith(
      expect.objectContaining({ projectId: "p1", offset: 0, limit: 50 }),
    );
  });
});
