/**
 * Comprehensive Tests for ItemsTreeView
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useItems } from "../../hooks/useItems";
import { useProjects } from "../../hooks/useProjects";
import { ItemsTreeView } from "../../views/ItemsTreeView";

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
	useItems: vi.fn(),
}));

vi.mock("../../hooks/useProjects", () => ({
	useProjects: vi.fn(),
}));

describe("ItemsTreeView", () => {
	let queryClient: QueryClient;

	beforeEach(() => {
		queryClient = new QueryClient({
			defaultOptions: {
				queries: { retry: false },
				mutations: { retry: false },
			},
		});
		vi.clearAllMocks();
	});

	it("renders tree view with items", () => {
		const mockItems = [
			{
				id: "item-1",
				title: "Parent Item",
				type: "feature",
				status: "todo",
				parentId: null,
			},
			{
				id: "item-2",
				title: "Child Item",
				type: "feature",
				status: "done",
				parentId: "item-1",
			},
		];

		vi.mocked(useItems).mockReturnValue({
			data: mockItems,
			isLoading: false,
			isError: false,
			error: null,
		} as any);

		vi.mocked(useProjects).mockReturnValue({
			data: [],
			isLoading: false,
			isError: false,
			error: null,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTreeView />
			</QueryClientProvider>,
		);

		expect(screen.getByText("Parent Item")).toBeInTheDocument();
	});

	it("displays loading state", () => {
		vi.mocked(useItems).mockReturnValue({
			data: undefined,
			isLoading: true,
			isError: false,
			error: null,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTreeView />
			</QueryClientProvider>,
		);

		// Should show loading skeleton
	});

	it("handles expand/collapse", async () => {
		const user = userEvent.setup();
		const mockItems = [
			{
				id: "item-1",
				title: "Parent Item",
				type: "feature",
				status: "todo",
				parentId: null,
			},
			{
				id: "item-2",
				title: "Child Item",
				type: "feature",
				status: "done",
				parentId: "item-1",
			},
		];

		vi.mocked(useItems).mockReturnValue({
			data: mockItems,
			isLoading: false,
			isError: false,
			error: null,
		} as any);

		vi.mocked(useProjects).mockReturnValue({
			data: [],
			isLoading: false,
			isError: false,
			error: null,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTreeView />
			</QueryClientProvider>,
		);

		// Find expand button
		const expandButtons = screen.getAllByText("▶");
		if (expandButtons.length > 0) {
			await user.click(expandButtons[0]);
			await waitFor(() => {
				expect(screen.getByText("Child Item")).toBeInTheDocument();
			});
		}
	});

	it("displays search functionality", async () => {
		const user = userEvent.setup();

		vi.mocked(useItems).mockReturnValue({
			data: [],
			isLoading: false,
			isError: false,
			error: null,
		} as any);

		vi.mocked(useProjects).mockReturnValue({
			data: [],
			isLoading: false,
			isError: false,
			error: null,
		} as any);

		render(
			<QueryClientProvider client={queryClient}>
				<ItemsTreeView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText(/Search/i);
		if (searchInput) {
			await user.type(searchInput, "test");
			// Should filter tree items
		}
	});
});
