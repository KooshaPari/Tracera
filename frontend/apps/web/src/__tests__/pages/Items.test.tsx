/**
 * Comprehensive Items Page Tests
 * Tests: Items list, filtering, kanban view, tree view, CRUD operations
 */

import { QueryClient } from "@tanstack/react-query";
import {
	createMemoryHistory,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { routeTree } from "@/routeTree.gen";

vi.mock("@/api/items", () => ({
	fetchItems: vi.fn(),
	createItem: vi.fn(),
	updateItem: vi.fn(),
	deleteItem: vi.fn(),
	bulkUpdateItems: vi.fn(),
}));

describe("Items Page", () => {
	let queryClient: QueryClient;
	let router: any;
	let history: any;

	beforeEach(() => {
		queryClient = new QueryClient({
			defaultOptions: {
				queries: { retry: false, gcTime: 0 },
				mutations: { retry: false },
			},
		});

		history = createMemoryHistory({
			initialEntries: ["/items"],
		});

		router = createRouter({
			routeTree,
			history,
			context: { queryClient },
		});

		vi.clearAllMocks();
	});

	afterEach(() => {
		queryClient.clear();
	});

	describe("Page Rendering", () => {
		it("renders items page with table view", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{
						id: "1",
						title: "Feature A",
						type: "feature",
						status: "active",
						priority: "high",
					},
					{
						id: "2",
						title: "Bug B",
						type: "bug",
						status: "done",
						priority: "critical",
					},
				],
				total: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("heading", { name: /all items/i }),
				).toBeInTheDocument();
			});

			expect(screen.getByText(/Feature A/i)).toBeInTheDocument();
			expect(screen.getByText(/Bug B/i)).toBeInTheDocument();
		});

		it("displays item metadata in table", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{
						id: "1",
						title: "Complete Feature",
						type: "feature",
						status: "in-progress",
						priority: "high",
						assignee: "John Doe",
						created_at: "2024-01-15",
						updated_at: "2024-02-20",
					},
				],
				total: 1,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Complete Feature/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/feature/i)).toBeInTheDocument();
			expect(screen.getByText(/in-progress/i)).toBeInTheDocument();
			expect(screen.getByText(/high/i)).toBeInTheDocument();
			expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
		});

		it("shows view toggle buttons", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /table view/i }),
				).toBeInTheDocument();
			});

			expect(
				screen.getByRole("button", { name: /kanban view/i }),
			).toBeInTheDocument();
			expect(
				screen.getByRole("button", { name: /tree view/i }),
			).toBeInTheDocument();
		});
	});

	describe("View Switching", () => {
		it("switches to kanban view", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Todo Item", status: "todo" },
					{ id: "2", title: "In Progress Item", status: "in-progress" },
					{ id: "3", title: "Done Item", status: "done" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Todo Item/i)).toBeInTheDocument();
			});

			const kanbanButton = screen.getByRole("button", { name: /kanban view/i });
			await userEvent.click(kanbanButton);

			await waitFor(() => {
				expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
			});

			expect(screen.getByText(/todo/i)).toBeInTheDocument();
			expect(screen.getByText(/in progress/i)).toBeInTheDocument();
			expect(screen.getByText(/done/i)).toBeInTheDocument();
		});

		it("switches to tree view", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Parent Item", parentId: null },
					{ id: "2", title: "Child Item", parentId: "1" },
					{ id: "3", title: "Grandchild Item", parentId: "2" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Parent Item/i)).toBeInTheDocument();
			});

			const treeButton = screen.getByRole("button", { name: /tree view/i });
			await userEvent.click(treeButton);

			await waitFor(() => {
				expect(screen.getByTestId("tree-view")).toBeInTheDocument();
			});

			const parentNode = screen.getByText(/Parent Item/i);
			expect(parentNode).toBeInTheDocument();
		});

		it("persists view selection in URL", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /kanban view/i }),
				).toBeInTheDocument();
			});

			const kanbanButton = screen.getByRole("button", { name: /kanban view/i });
			await userEvent.click(kanbanButton);

			await waitFor(() => {
				expect(history.location.search).toContain("view=kanban");
			});
		});
	});

	describe("Filtering", () => {
		it("filters by item type", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Feature Item", type: "feature" },
					{ id: "2", title: "Bug Item", type: "bug" },
					{ id: "3", title: "Doc Item", type: "doc" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Feature Item/i)).toBeInTheDocument();
			});

			const typeFilter = screen.getByRole("combobox", {
				name: /filter by type/i,
			});
			await userEvent.click(typeFilter);
			await userEvent.click(screen.getByRole("option", { name: /^feature$/i }));

			await waitFor(() => {
				expect(screen.getByText(/Feature Item/i)).toBeInTheDocument();
				expect(screen.queryByText(/Bug Item/i)).not.toBeInTheDocument();
				expect(screen.queryByText(/Doc Item/i)).not.toBeInTheDocument();
			});
		});

		it("filters by status", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Active Item", status: "active" },
					{ id: "2", title: "Done Item", status: "done" },
					{ id: "3", title: "Blocked Item", status: "blocked" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Active Item/i)).toBeInTheDocument();
			});

			const statusFilter = screen.getByRole("combobox", {
				name: /filter by status/i,
			});
			await userEvent.click(statusFilter);
			await userEvent.click(screen.getByRole("option", { name: /^active$/i }));

			await waitFor(() => {
				expect(screen.getByText(/Active Item/i)).toBeInTheDocument();
				expect(screen.queryByText(/Done Item/i)).not.toBeInTheDocument();
				expect(screen.queryByText(/Blocked Item/i)).not.toBeInTheDocument();
			});
		});

		it("filters by priority", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Critical Item", priority: "critical" },
					{ id: "2", title: "High Item", priority: "high" },
					{ id: "3", title: "Low Item", priority: "low" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Critical Item/i)).toBeInTheDocument();
			});

			const priorityFilter = screen.getByRole("combobox", {
				name: /filter by priority/i,
			});
			await userEvent.click(priorityFilter);
			await userEvent.click(screen.getByRole("option", { name: /critical/i }));

			await waitFor(() => {
				expect(screen.getByText(/Critical Item/i)).toBeInTheDocument();
				expect(screen.queryByText(/High Item/i)).not.toBeInTheDocument();
				expect(screen.queryByText(/Low Item/i)).not.toBeInTheDocument();
			});
		});

		it("filters by assignee", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "John Item", assignee: "John Doe" },
					{ id: "2", title: "Jane Item", assignee: "Jane Smith" },
					{ id: "3", title: "Unassigned Item", assignee: null },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/John Item/i)).toBeInTheDocument();
			});

			const assigneeFilter = screen.getByRole("combobox", {
				name: /filter by assignee/i,
			});
			await userEvent.click(assigneeFilter);
			await userEvent.click(screen.getByRole("option", { name: /John Doe/i }));

			await waitFor(() => {
				expect(screen.getByText(/John Item/i)).toBeInTheDocument();
				expect(screen.queryByText(/Jane Item/i)).not.toBeInTheDocument();
				expect(screen.queryByText(/Unassigned Item/i)).not.toBeInTheDocument();
			});
		});

		it("combines multiple filters", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", type: "feature", status: "active", priority: "high" },
					{ id: "2", type: "bug", status: "active", priority: "high" },
					{ id: "3", type: "feature", status: "done", priority: "high" },
					{ id: "4", type: "feature", status: "active", priority: "low" },
				],
				total: 4,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items.length).toBe(4);
			});

			// Apply type filter
			const typeFilter = screen.getByRole("combobox", {
				name: /filter by type/i,
			});
			await userEvent.click(typeFilter);
			await userEvent.click(screen.getByRole("option", { name: /^feature$/i }));

			// Apply status filter
			const statusFilter = screen.getByRole("combobox", {
				name: /filter by status/i,
			});
			await userEvent.click(statusFilter);
			await userEvent.click(screen.getByRole("option", { name: /^active$/i }));

			// Apply priority filter
			const priorityFilter = screen.getByRole("combobox", {
				name: /filter by priority/i,
			});
			await userEvent.click(priorityFilter);
			await userEvent.click(screen.getByRole("option", { name: /high/i }));

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items.length).toBe(1);
				expect(items[0]).toHaveAttribute("data-testid", "item-1");
			});
		});

		it("clears all filters", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", type: "feature" },
					{ id: "2", type: "bug" },
				],
				total: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items.length).toBe(2);
			});

			// Apply filter
			const typeFilter = screen.getByRole("combobox", {
				name: /filter by type/i,
			});
			await userEvent.click(typeFilter);
			await userEvent.click(screen.getByRole("option", { name: /^feature$/i }));

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items.length).toBe(1);
			});

			// Clear filters
			const clearButton = screen.getByRole("button", {
				name: /clear filters/i,
			});
			await userEvent.click(clearButton);

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items.length).toBe(2);
			});
		});
	});

	describe("Sorting", () => {
		it("sorts by title ascending", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Zebra" },
					{ id: "2", title: "Alpha" },
					{ id: "3", title: "Beta" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Zebra/i)).toBeInTheDocument();
			});

			const sortSelect = screen.getByRole("combobox", { name: /sort by/i });
			await userEvent.click(sortSelect);
			await userEvent.click(
				screen.getByRole("option", { name: /title \(a-z\)/i }),
			);

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items[0]).toHaveTextContent(/Alpha/i);
				expect(items[1]).toHaveTextContent(/Beta/i);
				expect(items[2]).toHaveTextContent(/Zebra/i);
			});
		});

		it("sorts by priority", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Low", priority: "low" },
					{ id: "2", title: "Critical", priority: "critical" },
					{ id: "3", title: "High", priority: "high" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Low/i)).toBeInTheDocument();
			});

			const sortSelect = screen.getByRole("combobox", { name: /sort by/i });
			await userEvent.click(sortSelect);
			await userEvent.click(screen.getByRole("option", { name: /priority/i }));

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items[0]).toHaveTextContent(/Critical/i);
				expect(items[1]).toHaveTextContent(/High/i);
				expect(items[2]).toHaveTextContent(/Low/i);
			});
		});

		it("sorts by date created", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Oldest", created_at: "2024-01-01" },
					{ id: "2", title: "Newest", created_at: "2024-03-01" },
					{ id: "3", title: "Middle", created_at: "2024-02-01" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Oldest/i)).toBeInTheDocument();
			});

			const sortSelect = screen.getByRole("combobox", { name: /sort by/i });
			await userEvent.click(sortSelect);
			await userEvent.click(
				screen.getByRole("option", { name: /newest first/i }),
			);

			await waitFor(() => {
				const items = screen.getAllByTestId(/item-/);
				expect(items[0]).toHaveTextContent(/Newest/i);
				expect(items[1]).toHaveTextContent(/Middle/i);
				expect(items[2]).toHaveTextContent(/Oldest/i);
			});
		});
	});

	describe("Search", () => {
		it("searches items by title", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Authentication Feature" },
					{ id: "2", title: "Authorization Module" },
					{ id: "3", title: "UI Component" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Authentication Feature/i)).toBeInTheDocument();
			});

			const searchInput = screen.getByPlaceholderText(/search items/i);
			await userEvent.type(searchInput, "auth");

			await waitFor(() => {
				expect(screen.getByText(/Authentication Feature/i)).toBeInTheDocument();
				expect(screen.getByText(/Authorization Module/i)).toBeInTheDocument();
				expect(screen.queryByText(/UI Component/i)).not.toBeInTheDocument();
			});
		});

		it("debounces search input", async () => {
			vi.useFakeTimers();

			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByPlaceholderText(/search items/i),
				).toBeInTheDocument();
			});

			const searchInput = screen.getByPlaceholderText(/search items/i);
			await userEvent.type(searchInput, "test");

			expect(fetchItems).toHaveBeenCalledTimes(1); // Initial load

			vi.advanceTimersByTime(300);

			await waitFor(() => {
				expect(fetchItems).toHaveBeenCalledTimes(2);
			});

			vi.useRealTimers();
		});
	});

	describe("Item Creation", () => {
		it("opens create item dialog", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /create item/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /create item/i }),
			);

			await waitFor(() => {
				expect(
					screen.getByRole("dialog", { name: /create item/i }),
				).toBeInTheDocument();
			});
		});

		it("creates new item successfully", async () => {
			const { fetchItems, createItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(createItem).mockResolvedValue({
				id: "new-item",
				title: "New Feature",
				type: "feature",
				status: "todo",
				priority: "medium",
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /create item/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /create item/i }),
			);

			await waitFor(() => {
				expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
			});

			await userEvent.type(screen.getByLabelText(/title/i), "New Feature");
			await userEvent.click(screen.getByLabelText(/type/i));
			await userEvent.click(screen.getByRole("option", { name: /feature/i }));
			await userEvent.click(screen.getByLabelText(/priority/i));
			await userEvent.click(screen.getByRole("option", { name: /medium/i }));

			await userEvent.click(screen.getByRole("button", { name: /create$/i }));

			await waitFor(() => {
				expect(
					screen.getByText(/item created successfully/i),
				).toBeInTheDocument();
			});
		});

		it("validates required fields", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /create item/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /create item/i }),
			);

			await waitFor(() => {
				expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
			});

			await userEvent.click(screen.getByRole("button", { name: /create$/i }));

			await waitFor(() => {
				expect(screen.getByText(/title is required/i)).toBeInTheDocument();
			});
		});
	});

	describe("Item Editing", () => {
		it("opens edit dialog for item", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Edit Me", type: "feature" }],
				total: 1,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Edit Me/i)).toBeInTheDocument();
			});

			const editButton = screen.getByRole("button", { name: /edit item 1/i });
			await userEvent.click(editButton);

			await waitFor(() => {
				expect(
					screen.getByRole("dialog", { name: /edit item/i }),
				).toBeInTheDocument();
			});

			expect(screen.getByLabelText(/title/i)).toHaveValue("Edit Me");
		});

		it("updates item successfully", async () => {
			const { fetchItems, updateItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Old Title", type: "feature" }],
				total: 1,
			});
			vi.mocked(updateItem).mockResolvedValue({
				id: "1",
				title: "New Title",
				type: "feature",
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Old Title/i)).toBeInTheDocument();
			});

			const editButton = screen.getByRole("button", { name: /edit item 1/i });
			await userEvent.click(editButton);

			await waitFor(() => {
				expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
			});

			const titleInput = screen.getByLabelText(/title/i);
			await userEvent.clear(titleInput);
			await userEvent.type(titleInput, "New Title");

			await userEvent.click(screen.getByRole("button", { name: /save/i }));

			await waitFor(() => {
				expect(
					screen.getByText(/item updated successfully/i),
				).toBeInTheDocument();
			});
		});

		it("inline edits item field", async () => {
			const { fetchItems, updateItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Item", status: "todo" }],
				total: 1,
			});
			vi.mocked(updateItem).mockResolvedValue({
				id: "1",
				title: "Item",
				status: "in-progress",
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/todo/i)).toBeInTheDocument();
			});

			const statusCell = screen.getByTestId("item-1-status");
			await userEvent.click(statusCell);

			await waitFor(() => {
				expect(screen.getByRole("combobox")).toBeInTheDocument();
			});

			await userEvent.click(screen.getByRole("combobox"));
			await userEvent.click(
				screen.getByRole("option", { name: /in progress/i }),
			);

			await waitFor(() => {
				expect(screen.getByText(/in-progress/i)).toBeInTheDocument();
			});
		});
	});

	describe("Item Deletion", () => {
		it("deletes item with confirmation", async () => {
			const { fetchItems, deleteItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Delete Me" }],
				total: 1,
			});
			vi.mocked(deleteItem).mockResolvedValue({ success: true });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Delete Me/i)).toBeInTheDocument();
			});

			const deleteButton = screen.getByRole("button", {
				name: /delete item 1/i,
			});
			await userEvent.click(deleteButton);

			await waitFor(() => {
				expect(screen.getByText(/confirm delete/i)).toBeInTheDocument();
			});

			await userEvent.click(screen.getByRole("button", { name: /confirm/i }));

			await waitFor(() => {
				expect(screen.getByText(/item deleted/i)).toBeInTheDocument();
			});
		});

		it("cancels deletion", async () => {
			const { fetchItems, deleteItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Keep Me" }],
				total: 1,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Keep Me/i)).toBeInTheDocument();
			});

			const deleteButton = screen.getByRole("button", {
				name: /delete item 1/i,
			});
			await userEvent.click(deleteButton);

			await waitFor(() => {
				expect(screen.getByText(/confirm delete/i)).toBeInTheDocument();
			});

			await userEvent.click(screen.getByRole("button", { name: /cancel/i }));

			await waitFor(() => {
				expect(screen.queryByText(/confirm delete/i)).not.toBeInTheDocument();
			});

			expect(deleteItem).not.toHaveBeenCalled();
		});
	});

	describe("Bulk Operations", () => {
		it("selects multiple items", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Item 1" },
					{ id: "2", title: "Item 2" },
					{ id: "3", title: "Item 3" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("checkbox", { name: /select item 1/i }),
			);
			await userEvent.click(
				screen.getByRole("checkbox", { name: /select item 2/i }),
			);

			await waitFor(() => {
				expect(screen.getByText(/2 selected/i)).toBeInTheDocument();
			});
		});

		it("selects all items", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Item 1" },
					{ id: "2", title: "Item 2" },
				],
				total: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
			});

			const selectAllCheckbox = screen.getByRole("checkbox", {
				name: /select all/i,
			});
			await userEvent.click(selectAllCheckbox);

			await waitFor(() => {
				expect(screen.getByText(/2 selected/i)).toBeInTheDocument();
			});
		});

		it("bulk updates status", async () => {
			const { fetchItems, bulkUpdateItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Item 1", status: "todo" },
					{ id: "2", title: "Item 2", status: "todo" },
				],
				total: 2,
			});
			vi.mocked(bulkUpdateItems).mockResolvedValue({
				updated: ["1", "2"],
				count: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("checkbox", { name: /select all/i }),
			);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /bulk actions/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /bulk actions/i }),
			);
			await userEvent.click(
				screen.getByRole("menuitem", { name: /change status/i }),
			);

			await waitFor(() => {
				expect(screen.getByLabelText(/new status/i)).toBeInTheDocument();
			});

			await userEvent.click(screen.getByLabelText(/new status/i));
			await userEvent.click(
				screen.getByRole("option", { name: /in progress/i }),
			);

			await userEvent.click(screen.getByRole("button", { name: /apply/i }));

			await waitFor(() => {
				expect(screen.getByText(/2 items updated/i)).toBeInTheDocument();
			});
		});

		it("bulk deletes items", async () => {
			const { fetchItems, deleteItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Item 1" },
					{ id: "2", title: "Item 2" },
				],
				total: 2,
			});
			vi.mocked(deleteItem).mockResolvedValue({ success: true });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("checkbox", { name: /select all/i }),
			);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /bulk actions/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /bulk actions/i }),
			);
			await userEvent.click(screen.getByRole("menuitem", { name: /delete/i }));

			await waitFor(() => {
				expect(screen.getByText(/delete 2 items/i)).toBeInTheDocument();
			});

			await userEvent.click(screen.getByRole("button", { name: /confirm/i }));

			await waitFor(() => {
				expect(screen.getByText(/2 items deleted/i)).toBeInTheDocument();
			});
		});
	});

	describe("Kanban View", () => {
		it("displays items in status columns", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Todo Item", status: "todo" },
					{ id: "2", title: "Progress Item", status: "in-progress" },
					{ id: "3", title: "Done Item", status: "done" },
				],
				total: 3,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /kanban view/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /kanban view/i }),
			);

			await waitFor(() => {
				const todoColumn = screen.getByTestId("kanban-column-todo");
				expect(within(todoColumn).getByText(/Todo Item/i)).toBeInTheDocument();
			});

			const progressColumn = screen.getByTestId("kanban-column-in-progress");
			expect(
				within(progressColumn).getByText(/Progress Item/i),
			).toBeInTheDocument();

			const doneColumn = screen.getByTestId("kanban-column-done");
			expect(within(doneColumn).getByText(/Done Item/i)).toBeInTheDocument();
		});

		it("drags item between columns", async () => {
			const { fetchItems, updateItem } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Movable Item", status: "todo" }],
				total: 1,
			});
			vi.mocked(updateItem).mockResolvedValue({
				id: "1",
				title: "Movable Item",
				status: "in-progress",
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /kanban view/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /kanban view/i }),
			);

			await waitFor(() => {
				const item = screen.getByTestId("kanban-item-1");
				expect(item).toBeInTheDocument();
			});

			// Simulate drag and drop (simplified)
			const item = screen.getByTestId("kanban-item-1");
			const targetColumn = screen.getByTestId("kanban-column-in-progress");

			// Use data-transfer simulation
			const dragStartEvent = new DragEvent("dragstart", { bubbles: true });
			item.dispatchEvent(dragStartEvent);

			const dropEvent = new DragEvent("drop", { bubbles: true });
			targetColumn.dispatchEvent(dropEvent);

			await waitFor(() => {
				expect(updateItem).toHaveBeenCalledWith("1", { status: "in-progress" });
			});
		});
	});

	describe("Accessibility", () => {
		it("has proper table accessibility", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [{ id: "1", title: "Item" }],
				total: 1,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByRole("table")).toBeInTheDocument();
			});

			expect(screen.getByRole("table")).toHaveAccessibleName();
			const headers = screen.getAllByRole("columnheader");
			expect(headers.length).toBeGreaterThan(0);
		});

		it("supports keyboard navigation", async () => {
			const { fetchItems } = await import("@/api/items");

			vi.mocked(fetchItems).mockResolvedValue({
				data: [
					{ id: "1", title: "Item 1" },
					{ id: "2", title: "Item 2" },
				],
				total: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
			});

			await userEvent.tab();
			expect(screen.getByTestId("item-row-1")).toHaveFocus();

			await userEvent.keyboard("{ArrowDown}");
			expect(screen.getByTestId("item-row-2")).toHaveFocus();
		});
	});
});
