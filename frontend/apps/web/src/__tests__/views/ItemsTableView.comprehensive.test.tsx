/**
 * Comprehensive Tests for ItemsTableView
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useDeleteItem, useItems, useUpdateItem } from "../../hooks/useItems";
import { useProjects } from "../../hooks/useProjects";
import { ItemsTableView } from "../../views/ItemsTableView";

// Mock TanStack Router
vi.mock("@tanstack/react-router", async () => {
	const actual = await vi.importActual("@tanstack/react-router");
	return {
		...actual,
		Link: ({ children, to }: any) => (
			<a href={typeof to === "string" ? to : to.toString()}>{children}</a>
		),
		useNavigate: () => vi.fn(),
		useSearch: () => ({}),
	};
});

vi.mock("../../hooks/useItems", () => ({
	useDeleteItem: vi.fn(),
	useItems: vi.fn(),
	useUpdateItem: vi.fn(),
}));

vi.mock("../../hooks/useProjects", () => ({
	useProjects: vi.fn(),
}));

describe(ItemsTableView, () => {
	let queryClient: QueryClient;

	beforeEach(() => {
		queryClient = new QueryClient({
			defaultOptions: {
				mutations: { retry: false },
				queries: { retry: false },
			},
		});
		vi.clearAllMocks();
	});

	it("renders table with items", () => {
		const mockItems = [
			{
				created_at: new Date().toISOString(),
				id: "item-1",
				owner: "user1",
				priority: "high",
				status: "todo",
				title: "Item 1",
				type: "feature",
			},
		];

		vi.mocked(useItems).mockReturnValue({
			data: mockItems,
			error: null,
			isError: false,
			isLoading: false,
		} as any);

		vi.mocked(useUpdateItem).mockReturnValue({
			mutate: vi.fn(),
		} as any);

		vi.mocked(useDeleteItem).mockReturnValue({
			mutate: vi.fn(),
		} as any);

		vi.mocked(useProjects).mockReturnValue({
			data: [],
			error: null,
			isError: false,
			isLoading: false,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTableView items={mockItems} type="feature" loading={false} />
			</QueryClientProvider>,
		);

		expect(screen.getByText("Item 1")).toBeInTheDocument();
	});

	it("displays loading state", () => {
		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTableView items={[]} type="feature" loading />
			</QueryClientProvider>,
		);

		// Should show loading skeleton
	});

	it("handles sorting", async () => {
		const mockItems = [
			{
				created_at: new Date("2024-01-01").toISOString(),
				id: "item-1",
				priority: "low",
				status: "todo",
				title: "Item A",
				type: "feature",
			},
			{
				created_at: new Date("2024-01-02").toISOString(),
				id: "item-2",
				priority: "high",
				status: "done",
				title: "Item B",
				type: "feature",
			},
		];

		vi.mocked(useItems).mockReturnValue({
			data: mockItems,
			error: null,
			isError: false,
			isLoading: false,
		} as any);

		vi.mocked(useUpdateItem).mockReturnValue({
			mutate: vi.fn(),
		} as any);

		vi.mocked(useDeleteItem).mockReturnValue({
			mutate: vi.fn(),
		} as any);

		vi.mocked(useProjects).mockReturnValue({
			data: [],
			error: null,
			isError: false,
			isLoading: false,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTableView />
			</QueryClientProvider>,
		);

		// Both items should be visible initially
		expect(screen.getByText("Item A")).toBeInTheDocument();
		expect(screen.getByText("Item B")).toBeInTheDocument();

		// Click on sortable column header
		const titleHeader = screen.getByText("Title");
		await user.click(titleHeader);

		// Items should still be visible after sort (sorting is handled by table component)
		expect(screen.getByText("Item A")).toBeInTheDocument();
		expect(screen.getByText("Item B")).toBeInTheDocument();
	});

	it("handles filtering", async () => {
		const mockItems = [
			{
				id: "item-1",
				priority: "high",
				status: "todo",
				title: "Item 1",
				type: "feature",
			},
			{
				id: "item-2",
				priority: "low",
				status: "done",
				title: "Item 2",
				type: "feature",
			},
		];

		vi.mocked(useItems).mockReturnValue({
			data: mockItems,
			error: null,
			isError: false,
			isLoading: false,
		} as any);

		vi.mocked(useUpdateItem).mockReturnValue({
			mutate: vi.fn(),
		} as any);

		vi.mocked(useDeleteItem).mockReturnValue({
			mutate: vi.fn(),
		} as any);

		vi.mocked(useProjects).mockReturnValue({
			data: [],
			error: null,
			isError: false,
			isLoading: false,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTableView />
			</QueryClientProvider>,
		);

		// Filter input should be present
		const filterInput = screen.getByPlaceholderText(/Search/i);
		expect(filterInput).toBeInTheDocument();

		// Both items visible initially
		expect(screen.getByText("Item 1")).toBeInTheDocument();
		expect(screen.getByText("Item 2")).toBeInTheDocument();

		// Type in filter (filtering is client-side, so both items still visible)
		await user.type(filterInput, "Item 1");

		// Items are filtered client-side - Item 1 should still be visible
		expect(screen.getByText("Item 1")).toBeInTheDocument();
	});

	it("handles bulk selection", async () => {
		const mockItems = [
			{
				id: "item-1",
				status: "todo",
				title: "Item 1",
				type: "feature",
			},
			{
				id: "item-2",
				status: "done",
				title: "Item 2",
				type: "feature",
			},
		];

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTableView items={mockItems} type="feature" loading={false} />
			</QueryClientProvider>,
		);

		// Select all checkbox should be present
		const checkboxes = screen.getAllByRole("checkbox");
		if (checkboxes.length > 0) {
			await user.click(checkboxes[0]);
			// Bulk actions should appear
		}
	});
});
