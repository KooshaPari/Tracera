/**
 * Comprehensive Dashboard Page Tests
 * Tests: Dashboard rendering, data fetching, loading states, error handling, navigation
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

// Mock API modules
vi.mock("@/api/projects", () => ({
	fetchProjects: vi.fn(),
}));

vi.mock("@/api/items", () => ({
	fetchRecentItems: vi.fn(),
}));

vi.mock("@/api/system", () => ({
	fetchSystemStatus: vi.fn(),
}));

describe("Dashboard Page", () => {
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
			initialEntries: ["/"],
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
		it("renders dashboard page with main sections", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{
						id: "1",
						name: "Project Alpha",
						status: "active",
						created_at: "2024-01-01",
					},
					{
						id: "2",
						name: "Project Beta",
						status: "active",
						created_at: "2024-01-02",
					},
				],
				total: 2,
			});

			vi.mocked(fetchRecentItems).mockResolvedValue({
				data: [
					{ id: "i1", title: "Item 1", type: "feature", status: "active" },
					{ id: "i2", title: "Item 2", type: "bug", status: "resolved" },
				],
				total: 2,
			});

			vi.mocked(fetchSystemStatus).mockResolvedValue({
				status: "healthy",
				uptime: 99.9,
				activeAgents: 5,
				queuedJobs: 12,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
			});

			// Check for main sections
			expect(screen.getByText(/Project Alpha/i)).toBeInTheDocument();
			expect(screen.getByText(/Project Beta/i)).toBeInTheDocument();
			expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
			expect(screen.getByText(/Item 2/i)).toBeInTheDocument();
		});

		it("renders system status indicators", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({
				status: "healthy",
				uptime: 99.9,
				activeAgents: 25,
				queuedJobs: 150,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/99.9/)).toBeInTheDocument();
			});

			expect(screen.getByText(/25/)).toBeInTheDocument();
			expect(screen.getByText(/150/)).toBeInTheDocument();
		});

		it("renders quick action buttons", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /create project/i }),
				).toBeInTheDocument();
			});

			expect(
				screen.getByRole("button", { name: /new item/i }),
			).toBeInTheDocument();
			expect(
				screen.getByRole("button", { name: /search/i }),
			).toBeInTheDocument();
		});

		it("renders recent activity timeline", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({
				data: [
					{
						id: "i1",
						title: "Bug Fix",
						type: "bug",
						updated_at: "2024-01-10T10:00:00Z",
					},
					{
						id: "i2",
						title: "Feature Request",
						type: "feature",
						updated_at: "2024-01-10T09:00:00Z",
					},
					{
						id: "i3",
						title: "Documentation",
						type: "doc",
						updated_at: "2024-01-10T08:00:00Z",
					},
				],
				total: 3,
			});
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Bug Fix/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/Feature Request/i)).toBeInTheDocument();
			expect(screen.getByText(/Documentation/i)).toBeInTheDocument();
		});

		it("displays project statistics cards", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{ id: "1", name: "Project 1", itemCount: 50, linkCount: 100 },
					{ id: "2", name: "Project 2", itemCount: 30, linkCount: 60 },
				],
				total: 2,
				totalItems: 80,
				totalLinks: 160,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/80/)).toBeInTheDocument(); // Total items
			});

			expect(screen.getByText(/160/)).toBeInTheDocument(); // Total links
		});
	});

	describe("Loading States", () => {
		it("shows loading skeleton on initial load", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			// Delay response to see loading state
			vi.mocked(fetchProjects).mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(() => resolve({ data: [], total: 0 }), 100),
					),
			);
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			// Check for loading indicators
			const loadingElements = screen.getAllByRole("status", {
				name: /loading/i,
			});
			expect(loadingElements.length).toBeGreaterThan(0);

			await waitFor(() => {
				expect(
					screen.queryByRole("status", { name: /loading/i }),
				).not.toBeInTheDocument();
			});
		});

		it("shows loading for individual sections independently", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(() => resolve({ data: [], total: 0 }), 100),
					),
			);
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				const projectSection = screen.getByTestId("projects-section");
				expect(
					within(projectSection).queryByRole("status"),
				).not.toBeInTheDocument();
			});

			const itemsSection = screen.getByTestId("recent-items-section");
			expect(within(itemsSection).getByRole("status")).toBeInTheDocument();
		});

		it("handles stale data with background refetch indicators", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			const mockData = { data: [{ id: "1", name: "Project 1" }], total: 1 };
			vi.mocked(fetchProjects).mockResolvedValue(mockData);
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
			});

			// Trigger refetch
			queryClient.invalidateQueries({ queryKey: ["projects"] });

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [{ id: "1", name: "Project 1 Updated" }],
				total: 1,
			});

			await waitFor(() => {
				expect(screen.getByText(/Project 1 Updated/i)).toBeInTheDocument();
			});
		});
	});

	describe("Error Handling", () => {
		it("displays error message when projects fail to load", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockRejectedValue(
				new Error("Failed to fetch projects"),
			);
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByText(/failed to fetch projects/i),
				).toBeInTheDocument();
			});

			expect(
				screen.getByRole("button", { name: /retry/i }),
			).toBeInTheDocument();
		});

		it("displays error when system status fails", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockRejectedValue(
				new Error("System unavailable"),
			);

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/system unavailable/i)).toBeInTheDocument();
			});
		});

		it("shows partial content when some requests fail", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [{ id: "1", name: "Project Alpha" }],
				total: 1,
			});
			vi.mocked(fetchRecentItems).mockRejectedValue(new Error("Items failed"));
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Project Alpha/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/items failed/i)).toBeInTheDocument();
		});

		it("allows retry on failed sections", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects)
				.mockRejectedValueOnce(new Error("Network error"))
				.mockResolvedValueOnce({
					data: [{ id: "1", name: "Project Recovered" }],
					total: 1,
				});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/network error/i)).toBeInTheDocument();
			});

			const retryButton = screen.getByRole("button", { name: /retry/i });
			await userEvent.click(retryButton);

			await waitFor(() => {
				expect(screen.getByText(/Project Recovered/i)).toBeInTheDocument();
			});
		});

		it("displays 404 error for non-existent routes", async () => {
			history.push("/nonexistent-route");

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/404/i)).toBeInTheDocument();
			});

			expect(screen.getByText(/page not found/i)).toBeInTheDocument();
		});
	});

	describe("User Navigation", () => {
		it("navigates to project detail when clicking project card", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [{ id: "proj-123", name: "Target Project", status: "active" }],
				total: 1,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Target Project/i)).toBeInTheDocument();
			});

			const projectCard = screen.getByTestId("project-card-proj-123");
			await userEvent.click(projectCard);

			await waitFor(() => {
				expect(history.location.pathname).toBe("/projects/proj-123");
			});
		});

		it('navigates to projects list when clicking "View All Projects"', async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/view all projects/i)).toBeInTheDocument();
			});

			const viewAllButton = screen.getByRole("link", {
				name: /view all projects/i,
			});
			await userEvent.click(viewAllButton);

			await waitFor(() => {
				expect(history.location.pathname).toBe("/projects");
			});
		});

		it("navigates to search when clicking search button", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /search/i }),
				).toBeInTheDocument();
			});

			const searchButton = screen.getByRole("button", { name: /search/i });
			await userEvent.click(searchButton);

			await waitFor(() => {
				expect(history.location.pathname).toBe("/search");
			});
		});

		it("opens create project modal from quick action", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /create project/i }),
				).toBeInTheDocument();
			});

			const createButton = screen.getByRole("button", {
				name: /create project/i,
			});
			await userEvent.click(createButton);

			await waitFor(() => {
				expect(
					screen.getByRole("dialog", { name: /create project/i }),
				).toBeInTheDocument();
			});
		});

		it("navigates to item detail from recent activity", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({
				data: [
					{
						id: "item-456",
						title: "Recent Item",
						type: "feature",
						projectId: "proj-123",
					},
				],
				total: 1,
			});
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Recent Item/i)).toBeInTheDocument();
			});

			const itemLink = screen.getByTestId("item-link-item-456");
			await userEvent.click(itemLink);

			await waitFor(() => {
				expect(history.location.pathname).toContain("item-456");
			});
		});
	});

	describe("Data Refresh", () => {
		it("refreshes data when refresh button clicked", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValueOnce({
				data: [{ id: "1", name: "Old Project" }],
				total: 1,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Old Project/i)).toBeInTheDocument();
			});

			vi.mocked(fetchProjects).mockResolvedValueOnce({
				data: [{ id: "1", name: "New Project" }],
				total: 1,
			});

			const refreshButton = screen.getByRole("button", { name: /refresh/i });
			await userEvent.click(refreshButton);

			await waitFor(() => {
				expect(screen.getByText(/New Project/i)).toBeInTheDocument();
			});
		});

		it("auto-refreshes data at configured intervals", async () => {
			vi.useFakeTimers();

			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			let callCount = 0;
			vi.mocked(fetchProjects).mockImplementation(async () => {
				callCount++;
				return { data: [{ id: "1", name: `Project ${callCount}` }], total: 1 };
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
			});

			// Advance timer by refetch interval (e.g., 30 seconds)
			vi.advanceTimersByTime(30000);

			await waitFor(() => {
				expect(screen.getByText(/Project 2/i)).toBeInTheDocument();
			});

			vi.useRealTimers();
		});
	});

	describe("Accessibility", () => {
		it("has proper ARIA labels on interactive elements", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(
					screen.getByRole("button", { name: /create project/i }),
				).toHaveAttribute("aria-label");
			});

			expect(screen.getByRole("button", { name: /search/i })).toHaveAttribute(
				"aria-label",
			);
			expect(screen.getByRole("button", { name: /refresh/i })).toHaveAttribute(
				"aria-label",
			);
		});

		it("supports keyboard navigation", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{ id: "1", name: "Project 1" },
					{ id: "2", name: "Project 2" },
				],
				total: 2,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Project 1/i)).toBeInTheDocument();
			});

			// Tab through interactive elements
			await userEvent.tab();
			expect(screen.getByTestId("project-card-1")).toHaveFocus();

			await userEvent.tab();
			expect(screen.getByTestId("project-card-2")).toHaveFocus();

			// Enter to navigate
			await userEvent.keyboard("{Enter}");

			await waitFor(() => {
				expect(history.location.pathname).toBe("/projects/2");
			});
		});
	});

	describe("Search Integration", () => {
		it("shows command palette when Cmd+K pressed", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
			});

			await userEvent.keyboard("{Meta>}k{/Meta}");

			await waitFor(() => {
				expect(
					screen.getByRole("dialog", { name: /command palette/i }),
				).toBeInTheDocument();
			});
		});

		it("searches from dashboard quick search", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
			});

			const searchInput = screen.getByPlaceholderText(/search/i);
			await userEvent.type(searchInput, "test query{Enter}");

			await waitFor(() => {
				expect(history.location.pathname).toBe("/search");
				expect(history.location.search).toContain("q=test%20query");
			});
		});
	});

	describe("Real-time Updates", () => {
		it("displays notifications for new items", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
			});

			// Simulate websocket notification
			const event = new CustomEvent("item:created", {
				detail: { id: "new-item", title: "New Feature" },
			});
			window.dispatchEvent(event);

			await waitFor(() => {
				expect(screen.getByText(/new feature created/i)).toBeInTheDocument();
			});
		});

		it("updates system status in real-time", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({
				status: "healthy",
				activeAgents: 5,
			});

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/5/)).toBeInTheDocument();
			});

			// Simulate status update
			vi.mocked(fetchSystemStatus).mockResolvedValue({
				status: "healthy",
				activeAgents: 10,
			});

			queryClient.invalidateQueries({ queryKey: ["system-status"] });

			await waitFor(() => {
				expect(screen.getByText(/10/)).toBeInTheDocument();
			});
		});
	});

	describe("Empty States", () => {
		it("shows empty state when no projects exist", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/no projects yet/i)).toBeInTheDocument();
			});

			expect(
				screen.getByText(/get started by creating your first project/i),
			).toBeInTheDocument();
			expect(
				screen.getByRole("button", { name: /create project/i }),
			).toBeInTheDocument();
		});

		it("shows empty state for recent items", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [{ id: "1", name: "Project 1" }],
				total: 1,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/no recent activity/i)).toBeInTheDocument();
			});
		});
	});

	describe("Filters and Sorting", () => {
		it("filters projects by status", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{ id: "1", name: "Active Project", status: "active" },
					{ id: "2", name: "Archived Project", status: "archived" },
				],
				total: 2,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Active Project/i)).toBeInTheDocument();
			});

			const filterSelect = screen.getByRole("combobox", {
				name: /filter by status/i,
			});
			await userEvent.click(filterSelect);
			await userEvent.click(screen.getByRole("option", { name: /active/i }));

			await waitFor(() => {
				expect(screen.getByText(/Active Project/i)).toBeInTheDocument();
				expect(screen.queryByText(/Archived Project/i)).not.toBeInTheDocument();
			});
		});

		it("sorts projects by date", async () => {
			const { fetchProjects } = await import("@/api/projects");
			const { fetchRecentItems } = await import("@/api/items");
			const { fetchSystemStatus } = await import("@/api/system");

			vi.mocked(fetchProjects).mockResolvedValue({
				data: [
					{ id: "1", name: "Older Project", created_at: "2024-01-01" },
					{ id: "2", name: "Newer Project", created_at: "2024-02-01" },
				],
				total: 2,
			});
			vi.mocked(fetchRecentItems).mockResolvedValue({ data: [], total: 0 });
			vi.mocked(fetchSystemStatus).mockResolvedValue({ status: "healthy" });

			render(<RouterProvider router={router} />);

			await waitFor(() => {
				expect(screen.getByText(/Newer Project/i)).toBeInTheDocument();
			});

			const sortSelect = screen.getByRole("combobox", { name: /sort by/i });
			await userEvent.click(sortSelect);
			await userEvent.click(
				screen.getByRole("option", { name: /oldest first/i }),
			);

			await waitFor(() => {
				const projects = screen.getAllByTestId(/project-card/);
				expect(projects[0]).toHaveTextContent(/Older Project/i);
			});
		});
	});
});
