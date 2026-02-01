import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
	createRootRoute,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ItemsTableView } from "../ItemsTableView";

// Mock hooks
vi.mock("../../hooks/useItems", () => ({
	useItems: vi.fn(() => ({
		data: {
			items: Array.from({ length: 1000 }, (_, i) => ({
				id: `item-${i}`,
				title: `Item ${i}`,
				type: "feature",
				status: "todo" as const,
				priority: "medium" as const,
				owner: `Owner ${i % 5}`,
				createdAt: new Date(2024, 0, (i % 30) + 1).toISOString(),
			})),
		},
		isLoading: false,
	})),
	useDeleteItem: vi.fn(() => ({
		mutateAsync: vi.fn(),
		isPending: false,
	})),
	useCreateItem: vi.fn(() => ({
		mutateAsync: vi.fn(),
		isPending: false,
	})),
}));

vi.mock("../../hooks/useProjects", () => ({
	useProjects: vi.fn(() => ({
		data: [],
	})),
}));

// Setup router
const rootRoute = createRootRoute({
	component: () => <ItemsTableView />,
});

const router = createRouter({
	routeTree: rootRoute,
});

describe("ItemsTableView - Virtual Scrolling", () => {
	let queryClient: QueryClient;

	beforeEach(() => {
		queryClient = new QueryClient();
	});

	it("should render virtual table with 1000 items", async () => {
		const { container } = render(
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router}>
					<ItemsTableView />
				</RouterProvider>
			</QueryClientProvider>,
		);

		// Wait for items to load
		await screen.findByText(/Item 0/i);

		// Verify that the virtual container exists
		const virtualContainer = container.querySelector('[style*="height"]');
		expect(virtualContainer).toBeInTheDocument();
	});

	it("should only render visible rows (not all 1000)", async () => {
		const { container } = render(
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router}>
					<ItemsTableView />
				</RouterProvider>
			</QueryClientProvider>,
		);

		await screen.findByText(/Item 0/i);

		// Count rendered TableRow elements
		const rows = container.querySelectorAll("tbody tr");

		// Should be much less than 1000 (typically 10-20 visible + overscan)
		expect(rows.length).toBeLessThan(50);
		expect(rows.length).toBeGreaterThan(0);
	});

	it("should handle search filtering with virtual scrolling", async () => {
		const user = userEvent.setup();
		const { container } = render(
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router}>
					<ItemsTableView />
				</RouterProvider>
			</QueryClientProvider>,
		);

		await screen.findByText(/Item 0/i);

		// Search for a specific item
		const searchInput = screen.getByPlaceholderText(/Search identifiers/i);
		await user.type(searchInput, "Item 42");

		// Wait for filtered results
		await screen.findByText(/Item 42/i);

		// Verify only filtered items are in DOM
		const rows = container.querySelectorAll("tbody tr");
		expect(rows.length).toBeLessThan(10);
	});

	it("should handle sorting with virtual scrolling", async () => {
		const user = userEvent.setup();
		render(
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router}>
					<ItemsTableView />
				</RouterProvider>
			</QueryClientProvider>,
		);

		await screen.findByText(/Item 0/i);

		// Click sort button
		const sortButton = screen.getByRole("button", { name: /Node Identifier/i });
		await user.click(sortButton);

		// Verify results are still rendered
		await screen.findByText(/Item/i);
	});

	it("should display empty state when no items match filter", async () => {
		const user = userEvent.setup();
		render(
			<QueryClientProvider client={queryClient}>
				<RouterProvider router={router}>
					<ItemsTableView />
				</RouterProvider>
			</QueryClientProvider>,
		);

		await screen.findByText(/Item 0/i);

		// Search for non-existent item
		const searchInput = screen.getByPlaceholderText(/Search identifiers/i);
		await user.type(searchInput, "nonexistent-item-xyz");

		// Wait for empty state
		await screen.findByText(/Registry Vacant/i);
	});
});
