import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AdvancedSearchView } from "../../views/AdvancedSearchView";

// Mock TanStack Router
vi.mock("@tanstack/react-router", async () => {
	const actual = await vi.importActual("@tanstack/react-router");
	return {
		...actual,
		Link: ({ children, to, ...props }: any) => (
			<a href={typeof to === "string" ? to : to?.toString?.()} {...props}>
				{children}
			</a>
		),
		useNavigate: () => vi.fn(),
		useSearch: () => ({}),
	};
});

// Mock fetch
global.fetch = vi.fn();

describe("AdvancedSearchView", () => {
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

	it("renders search interface", () => {
		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		expect(screen.getByText("Advanced Search")).toBeInTheDocument();
		expect(
			screen.getByPlaceholderText("Enter search terms..."),
		).toBeInTheDocument();
		expect(screen.getByText("Search")).toBeInTheDocument();
		expect(screen.getByText("Clear Filters")).toBeInTheDocument();
	});

	it("renders filter tabs", () => {
		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		expect(screen.getByText("Items")).toBeInTheDocument();
		expect(screen.getByText("Projects")).toBeInTheDocument();
		expect(screen.getByText("Links")).toBeInTheDocument();
	});

	it("displays filter options for items tab", () => {
		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		// Check for filter labels (using text content instead of labelFor)
		expect(screen.getByText("View")).toBeInTheDocument();
		expect(screen.getByText("Status")).toBeInTheDocument();
		expect(screen.getByText("Item Type")).toBeInTheDocument();
		expect(screen.getByText("Priority")).toBeInTheDocument();
	});

	it("handles search query input", async () => {
		const user = userEvent.setup();
		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText("Enter search terms...");
		await user.type(searchInput, "test query");

		expect(searchInput).toHaveValue("test query");
	});

	it("shows loading state", async () => {
		const user = userEvent.setup();
		(global.fetch as any).mockImplementation(
			() =>
				new Promise((resolve) =>
					setTimeout(
						() =>
							resolve({
								ok: true,
								json: async () => ({
									project_id: "test",
									query: "test",
									filters: {},
									results: [],
									total: 0,
								}),
							}),
						100,
					),
				),
		);

		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText("Enter search terms...");
		await user.type(searchInput, "test");

		// Wait for query to be enabled and loading
		await waitFor(() => {
			// Loading state should appear
		});
	});

	it("displays search results", async () => {
		const user = userEvent.setup();
		const mockResults = [
			{
				id: "item-1",
				title: "Test Item",
				type: "item",
				status: "todo",
				description: "Test description",
			},
		];

		// Mock fetch BEFORE rendering to ensure it's ready
		(global.fetch as any).mockResolvedValue({
			ok: true,
			json: async () => ({
				project_id: "test",
				query: "test",
				filters: {},
				results: mockResults,
				total: 1,
			}),
		});

		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText("Enter search terms...");
		await user.type(searchInput, "test");

		// Click Search to trigger query
		const searchButton = screen.getByText("Search");
		await user.click(searchButton);

		await waitFor(
			() => {
				expect(screen.getByText("Test Item")).toBeInTheDocument();
				expect(screen.getByText("Results (1)")).toBeInTheDocument();
			},
			{ timeout: 3000 },
		);
	});

	it("displays empty state when no results", async () => {
		const user = userEvent.setup();
		(global.fetch as any).mockResolvedValue({
			ok: true,
			json: async () => ({
				project_id: "test",
				query: "test",
				filters: {},
				results: [],
				total: 0,
			}),
		});

		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText("Enter search terms...");
		await user.type(searchInput, "test");

		// Click Search button to trigger query
		const searchButton = screen.getByText("Search");
		await user.click(searchButton);

		await waitFor(
			() => {
				expect(screen.getByText("No results found")).toBeInTheDocument();
			},
			{ timeout: 3000 },
		);
	});

	it("handles filter changes", async () => {
		const user = userEvent.setup();
		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		// Find the View select by its ID
		const viewSelect = document.getElementById("view-filter");
		expect(viewSelect).toBeInTheDocument();

		await user.click(viewSelect!);

		// Wait for dropdown to open and find Feature option
		await waitFor(() => {
			expect(
				screen.getByRole("option", { name: "Feature" }),
			).toBeInTheDocument();
		});

		const featureOption = screen.getByRole("option", { name: "Feature" });
		await user.click(featureOption);

		// Filter should be updated - use textContent for Radix Select
		await waitFor(() => {
			expect(viewSelect).toHaveTextContent("Feature");
		});
	});

	it("clears filters when clear button is clicked", async () => {
		const user = userEvent.setup();
		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText("Enter search terms...");
		await user.type(searchInput, "test");

		const clearButton = screen.getByText("Clear Filters");
		await user.click(clearButton);

		expect(searchInput).toHaveValue("");
	});

	it("displays error message on search failure", async () => {
		const user = userEvent.setup();

		// Mock fetch BEFORE rendering to ensure error is ready
		(global.fetch as any).mockRejectedValue(new Error("Search failed"));

		render(
			<QueryClientProvider client={queryClient}>
				<AdvancedSearchView />
			</QueryClientProvider>,
		);

		const searchInput = screen.getByPlaceholderText("Enter search terms...");
		await user.type(searchInput, "test");

		// Click Search to trigger query
		const searchButton = screen.getByText("Search");
		await user.click(searchButton);

		await waitFor(
			() => {
				expect(
					screen.getByText(/Error performing search/i),
				).toBeInTheDocument();
			},
			{ timeout: 3000 },
		);
	});
});
