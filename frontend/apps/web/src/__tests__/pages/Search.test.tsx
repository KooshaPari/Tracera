/**
 * Comprehensive Search Page Tests
 * Tests: Search functionality, filters, results display, faceted search
 */

import { QueryClient } from "@tanstack/react-query";
import {
	createMemoryHistory,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { routeTree } from "@/routeTree.gen";

vi.mock("@/api/search", () => ({
	fetchSearchResults: vi.fn(),
	searchSuggestions: vi.fn(),
}));

vi.mock("@/api/projects", () => ({
	fetchProjects: vi.fn(),
}));

describe("Search Page", () => {
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
			initialEntries: ["/search?q=test"],
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
		it("renders search page with search input", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
			});

			expect(
				screen.getByRole("heading", { name: /search results/i }),
			).toBeInTheDocument();
		});

		it("displays search query in input", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "authentication",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				const input = screen.getByPlaceholderText(
					/search/i,
				) as HTMLInputElement;
				expect(input.value).toBe("authentication");
			});
		});

		it("shows search results count", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: Array.from({ length: 15 }, (_, i) => ({
					id: `result-${i}`,
					title: `Result ${i}`,
					type: "item",
				})),
				total: 150,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/150 results/i)).toBeInTheDocument();
			});
		});
	});

	describe("Search Results", () => {
		it("displays search results with highlighting", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{
						id: "r1",
						title: "User Authentication System",
						type: "feature",
						highlights: ["User <mark>Authentication</mark> System"],
						excerpt: "Implement secure <mark>authentication</mark> for users",
					},
				],
				total: 1,
				query: "authentication",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByText(/User Authentication System/i),
				).toBeInTheDocument();
			});

			const highlights = screen.getAllByText(/authentication/i);
			expect(highlights.length).toBeGreaterThan(0);
		});

		it("displays different result types", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{ id: "r1", title: "Feature Item", type: "feature" },
					{ id: "r2", title: "Bug Report", type: "bug" },
					{ id: "r3", title: "Documentation", type: "doc" },
					{ id: "r4", title: "Test Case", type: "test" },
				],
				total: 4,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Feature Item/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/Bug Report/i)).toBeInTheDocument();
			expect(screen.getByText(/Documentation/i)).toBeInTheDocument();
			expect(screen.getByText(/Test Case/i)).toBeInTheDocument();
		});

		it("shows result metadata", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{
						id: "r1",
						title: "Search Result",
						type: "feature",
						project: "Project Alpha",
						status: "active",
						updated_at: "2024-02-20T10:00:00Z",
					},
				],
				total: 1,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Search Result/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/Project Alpha/i)).toBeInTheDocument();
			expect(screen.getByText(/active/i)).toBeInTheDocument();
			expect(screen.getByText(/2024-02-20/i)).toBeInTheDocument();
		});

		it("navigates to result on click", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{
						id: "item-123",
						title: "Clickable Result",
						type: "feature",
						projectId: "proj-456",
					},
				],
				total: 1,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Clickable Result/i)).toBeInTheDocument();
			});

			const resultLink = screen.getByTestId("search-result-item-123");
			await userEvent.click(resultLink);

			await waitFor(() => {
				expect(history.location.pathname).toContain("item-123");
			});
		});
	});

	describe("Search Filters", () => {
		it("filters by result type", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{ id: "r1", title: "Feature", type: "feature" },
					{ id: "r2", title: "Bug", type: "bug" },
				],
				total: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Feature/i)).toBeInTheDocument();
			});

			const typeFilter = screen.getByRole("combobox", {
				name: /filter by type/i,
			});
			await userEvent.click(typeFilter);
			await userEvent.click(screen.getByRole("option", { name: /^feature$/i }));

			await waitFor(() => {
				expect(screen.getByText(/Feature/i)).toBeInTheDocument();
				expect(screen.queryByText(/Bug/i)).not.toBeInTheDocument();
			});
		});

		it("filters by project", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{
						id: "r1",
						title: "Result 1",
						projectId: "proj-1",
						project: "Project A",
					},
					{
						id: "r2",
						title: "Result 2",
						projectId: "proj-2",
						project: "Project B",
					},
				],
				total: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{ id: "proj-1", name: "Project A" },
					{ id: "proj-2", name: "Project B" },
				],
				total: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Result 1/i)).toBeInTheDocument();
			});

			const projectFilter = screen.getByRole("combobox", {
				name: /filter by project/i,
			});
			await userEvent.click(projectFilter);
			await userEvent.click(screen.getByRole("option", { name: /Project A/i }));

			await waitFor(() => {
				expect(screen.getByText(/Result 1/i)).toBeInTheDocument();
				expect(screen.queryByText(/Result 2/i)).not.toBeInTheDocument();
			});
		});

		it("filters by date range", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{ id: "r1", title: "Old Result", updated_at: "2023-01-01" },
					{ id: "r2", title: "New Result", updated_at: "2024-06-01" },
				],
				total: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Old Result/i)).toBeInTheDocument();
			});

			const dateFilter = screen.getByRole("button", {
				name: /filter by date/i,
			});
			await userEvent.click(dateFilter);

			const startDate = screen.getByLabelText(/start date/i);
			await userEvent.type(startDate, "2024-01-01");

			await waitFor(() => {
				expect(screen.getByText(/New Result/i)).toBeInTheDocument();
				expect(screen.queryByText(/Old Result/i)).not.toBeInTheDocument();
			});
		});

		it("combines multiple filters", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{
						id: "r1",
						type: "feature",
						projectId: "proj-1",
						updated_at: "2024-06-01",
					},
					{
						id: "r2",
						type: "bug",
						projectId: "proj-1",
						updated_at: "2024-06-01",
					},
					{
						id: "r3",
						type: "feature",
						projectId: "proj-2",
						updated_at: "2024-06-01",
					},
				],
				total: 3,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{ id: "proj-1", name: "Project A" },
					{ id: "proj-2", name: "Project B" },
				],
				total: 2,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				const results = screen.getAllByTestId(/search-result/);
				expect(results.length).toBe(3);
			});

			// Apply type filter
			const typeFilter = screen.getByRole("combobox", {
				name: /filter by type/i,
			});
			await userEvent.click(typeFilter);
			await userEvent.click(screen.getByRole("option", { name: /^feature$/i }));

			// Apply project filter
			const projectFilter = screen.getByRole("combobox", {
				name: /filter by project/i,
			});
			await userEvent.click(projectFilter);
			await userEvent.click(screen.getByRole("option", { name: /Project A/i }));

			await waitFor(() => {
				const results = screen.getAllByTestId(/search-result/);
				expect(results.length).toBe(1);
				expect(results[0]).toHaveAttribute("data-testid", "search-result-r1");
			});
		});

		it("clears all filters", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{ id: "r1", type: "feature" },
					{ id: "r2", type: "bug" },
				],
				total: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				const results = screen.getAllByTestId(/search-result/);
				expect(results.length).toBe(2);
			});

			// Apply filter
			const typeFilter = screen.getByRole("combobox", {
				name: /filter by type/i,
			});
			await userEvent.click(typeFilter);
			await userEvent.click(screen.getByRole("option", { name: /^feature$/i }));

			await waitFor(() => {
				const results = screen.getAllByTestId(/search-result/);
				expect(results.length).toBe(1);
			});

			// Clear filters
			const clearButton = screen.getByRole("button", {
				name: /clear filters/i,
			});
			await userEvent.click(clearButton);

			await waitFor(() => {
				const results = screen.getAllByTestId(/search-result/);
				expect(results.length).toBe(2);
			});
		});
	});

	describe("Search Suggestions", () => {
		it("shows suggestions while typing", async () => {
			const { fetchSearchResults, searchSuggestions } = await import(
				"@/api/search"
			);
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(searchSuggestions).mockResolvedValue({
				suggestions: ["authentication", "authorization", "auth module"],
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
			});

			const searchInput = screen.getByPlaceholderText(/search/i);
			await userEvent.type(searchInput, "auth");

			await waitFor(() => {
				expect(screen.getByText(/authentication/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/authorization/i)).toBeInTheDocument();
			expect(screen.getByText(/auth module/i)).toBeInTheDocument();
		});

		it("selects suggestion and searches", async () => {
			const { fetchSearchResults, searchSuggestions } = await import(
				"@/api/search"
			);
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(searchSuggestions).mockResolvedValue({
				suggestions: ["authentication system"],
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
			});

			const searchInput = screen.getByPlaceholderText(/search/i);
			await userEvent.type(searchInput, "auth");

			await waitFor(() => {
				expect(screen.getByText(/authentication system/i)).toBeInTheDocument();
			});

			const suggestion = screen.getByText(/authentication system/i);
			await userEvent.click(suggestion);

			await waitFor(() => {
				expect(history.location.search).toContain("q=authentication%20system");
			});
		});

		it("dismisses suggestions on Escape", async () => {
			const { fetchSearchResults, searchSuggestions } = await import(
				"@/api/search"
			);
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(searchSuggestions).mockResolvedValue({
				suggestions: ["authentication"],
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
			});

			const searchInput = screen.getByPlaceholderText(/search/i);
			await userEvent.type(searchInput, "auth");

			await waitFor(() => {
				expect(screen.getByText(/authentication/i)).toBeInTheDocument();
			});

			await userEvent.keyboard("{Escape}");

			await waitFor(() => {
				expect(screen.queryByText(/authentication/i)).not.toBeInTheDocument();
			});
		});
	});

	describe("Faceted Search", () => {
		it("displays facets with counts", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 100,
				query: "test",
				facets: {
					type: {
						feature: 45,
						bug: 30,
						doc: 25,
					},
					status: {
						active: 60,
						done: 40,
					},
				},
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/feature \(45\)/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/bug \(30\)/i)).toBeInTheDocument();
			expect(screen.getByText(/doc \(25\)/i)).toBeInTheDocument();
			expect(screen.getByText(/active \(60\)/i)).toBeInTheDocument();
			expect(screen.getByText(/done \(40\)/i)).toBeInTheDocument();
		});

		it("filters by clicking facet", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 100,
				query: "test",
				facets: {
					type: {
						feature: 45,
						bug: 30,
					},
				},
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/feature \(45\)/i)).toBeInTheDocument();
			});

			const facetButton = screen.getByRole("button", {
				name: /feature \(45\)/i,
			});
			await userEvent.click(facetButton);

			await waitFor(() => {
				expect(history.location.search).toContain("type=feature");
			});
		});
	});

	describe("Pagination", () => {
		it("displays pagination controls", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: Array.from({ length: 50 }, (_, i) => ({
					id: `r${i}`,
					title: `Result ${i}`,
				})),
				total: 200,
				page: 1,
				pageSize: 50,
				totalPages: 4,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/page 1 of 4/i)).toBeInTheDocument();
			});

			expect(
				screen.getByRole("button", { name: /next page/i }),
			).toBeInTheDocument();
			expect(
				screen.getByRole("button", { name: /previous page/i }),
			).toBeDisabled();
		});

		it("navigates to next page", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValueOnce({
				data: [{ id: "r1", title: "Page 1 Result" }],
				total: 100,
				page: 1,
				pageSize: 50,
				totalPages: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Page 1 Result/i)).toBeInTheDocument();
			});

			vi.mocked(fetchSearchResults).mockResolvedValueOnce({
				data: [{ id: "r51", title: "Page 2 Result" }],
				total: 100,
				page: 2,
				pageSize: 50,
				totalPages: 2,
				query: "test",
			});

			const nextButton = screen.getByRole("button", { name: /next page/i });
			await userEvent.click(nextButton);

			await waitFor(() => {
				expect(screen.getByText(/Page 2 Result/i)).toBeInTheDocument();
			});
		});
	});

	describe("Advanced Search", () => {
		it("opens advanced search dialog", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /advanced search/i }),
				).toBeInTheDocument();
			});

			const advancedButton = screen.getByRole("button", {
				name: /advanced search/i,
			});
			await userEvent.click(advancedButton);

			await waitFor(() => {
				expect(
					screen.getByRole("dialog", { name: /advanced search/i }),
				).toBeInTheDocument();
			});
		});

		it("builds complex query with AND/OR operators", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /advanced search/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(
				screen.getByRole("button", { name: /advanced search/i }),
			);

			await waitFor(() => {
				expect(
					screen.getByRole("dialog", { name: /advanced search/i }),
				).toBeInTheDocument();
			});

			// Build query: (feature OR bug) AND status:active
			await userEvent.type(screen.getByLabelText(/term 1/i), "feature");
			await userEvent.click(screen.getByLabelText(/operator/i));
			await userEvent.click(screen.getByRole("option", { name: /OR/i }));
			await userEvent.type(screen.getByLabelText(/term 2/i), "bug");

			await userEvent.click(
				screen.getByRole("button", { name: /add condition/i }),
			);
			await userEvent.type(screen.getByLabelText(/field/i), "status");
			await userEvent.type(screen.getByLabelText(/value/i), "active");

			await userEvent.click(screen.getByRole("button", { name: /search/i }));

			await waitFor(() => {
				expect(history.location.search).toContain(
					"q=%28feature+OR+bug%29+AND+status%3Aactive",
				);
			});
		});
	});

	describe("Empty States", () => {
		it("shows empty state for no results", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "nonexistent query",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/no results found/i)).toBeInTheDocument();
			});

			expect(
				screen.getByText(/try different search terms/i),
			).toBeInTheDocument();
		});

		it("shows empty state when no query provided", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			history.push("/search");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/enter a search query/i)).toBeInTheDocument();
			});
		});
	});

	describe("Loading States", () => {
		it("shows loading skeleton while searching", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(
							() => resolve({ data: [], total: 0, query: "test" }),
							100,
						),
					),
			);
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			expect(
				screen.getAllByRole("status", { name: /loading/i }).length,
			).toBeGreaterThan(0);

			await waitFor(() => {
				expect(
					screen.queryByRole("status", { name: /loading/i }),
				).not.toBeInTheDocument();
			});
		});

		it("shows search in progress indicator", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(
							() => resolve({ data: [], total: 0, query: "test" }),
							100,
						),
					),
			);
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/searching/i)).toBeInTheDocument();
			});
		});
	});

	describe("Error Handling", () => {
		it("displays error message on search failure", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockRejectedValue(
				new Error("Search service unavailable"),
			);
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByText(/search service unavailable/i),
				).toBeInTheDocument();
			});

			expect(
				screen.getByRole("button", { name: /retry/i }),
			).toBeInTheDocument();
		});

		it("retries search on error", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults)
				.mockRejectedValueOnce(new Error("Failed"))
				.mockResolvedValueOnce({
					data: [{ id: "r1", title: "Recovered Result" }],
					total: 1,
					query: "test",
				});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/failed/i)).toBeInTheDocument();
			});

			const retryButton = screen.getByRole("button", { name: /retry/i });
			await userEvent.click(retryButton);

			await waitFor(() => {
				expect(screen.getByText(/Recovered Result/i)).toBeInTheDocument();
			});
		});
	});

	describe("Keyboard Shortcuts", () => {
		it("focuses search input on /", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
			});

			await userEvent.keyboard("/");

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toHaveFocus();
			});
		});

		it("navigates results with arrow keys", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{ id: "r1", title: "Result 1" },
					{ id: "r2", title: "Result 2" },
				],
				total: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Result 1/i)).toBeInTheDocument();
			});

			await userEvent.keyboard("{ArrowDown}");
			expect(screen.getByTestId("search-result-r1")).toHaveFocus();

			await userEvent.keyboard("{ArrowDown}");
			expect(screen.getByTestId("search-result-r2")).toHaveFocus();
		});
	});

	describe("Export Results", () => {
		it("exports search results to CSV", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [
					{ id: "r1", title: "Result 1", type: "feature" },
					{ id: "r2", title: "Result 2", type: "bug" },
				],
				total: 2,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Result 1/i)).toBeInTheDocument();
			});

			const exportButton = screen.getByRole("button", { name: /export/i });
			await userEvent.click(exportButton);

			await waitFor(() => {
				expect(
					screen.getByRole("menuitem", { name: /csv/i }),
				).toBeInTheDocument();
			});

			await userEvent.click(screen.getByRole("menuitem", { name: /csv/i }));

			// Check download was triggered
			await waitFor(() => {
				expect(screen.getByText(/export started/i)).toBeInTheDocument();
			});
		});
	});

	describe("Accessibility", () => {
		it("has proper ARIA labels", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [],
				total: 0,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByRole("search")).toBeInTheDocument();
			});

			expect(screen.getByRole("searchbox")).toHaveAttribute("aria-label");
			expect(
				screen.getByRole("region", { name: /search results/i }),
			).toBeInTheDocument();
		});

		it("announces search results count", async () => {
			const { fetchSearchResults } = await import("@/api/search");
			const { fetchProjects } = await import("@/api/projects");

			vi.mocked(fetchSearchResults).mockResolvedValue({
				data: [{ id: "r1", title: "Result" }],
				total: 1,
				query: "test",
			});
			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("status", { name: /search results/i }),
				).toHaveTextContent("1 result");
			});
		});
	});
});
