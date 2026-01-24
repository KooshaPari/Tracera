/**
 * Tests for Test View Route
 */

import { QueryClient } from "@tanstack/react-query";
import {
	createMemoryHistory,
	createRouter,
	RouterProvider,
} from "@tanstack/react-router";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { routeTree } from "@/routeTree.gen";

vi.mock("@/api/endpoints", () => ({
	projectsApi: {
		get: vi.fn(),
	},
	itemsApi: {
		list: vi.fn(),
	},
}));

describe("Test View Route", () => {
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

		vi.clearAllMocks();
	});

	it("renders test view with project data", async () => {
		const { fetchProject } = await import("@/api/projects");
		const { fetchProjectTests } = await import("@/api/items");

		(fetchProject as any).mockResolvedValue({
			id: "proj-1",
			name: "Test Project",
			description: "Test description",
		});

		(fetchProjectTests as any).mockResolvedValue([
			{
				id: "item-1",
				title: "Test Case 1",
				type: "test",
				status: "done",
				coverage: 85,
			},
		]);

		history = createMemoryHistory({
			initialEntries: ["/projects/proj-1/views/test"],
		});

		router = createRouter({
			routeTree,
			history,
			context: { queryClient },
		});

		render(<RouterProvider router={router} />);

		await waitFor(() => {
			expect(screen.getByText("Test Coverage")).toBeInTheDocument();
			expect(
				screen.getByText(/Test cases and coverage metrics/i),
			).toBeInTheDocument();
		});
	});

	it("displays project name in description", async () => {
		const { fetchProject } = await import("@/api/projects");
		const { fetchProjectTests } = await import("@/api/items");

		(fetchProject as any).mockResolvedValue({
			id: "proj-1",
			name: "Testing Project",
			description: "Test description",
		});

		(fetchProjectTests as any).mockResolvedValue([]);

		history = createMemoryHistory({
			initialEntries: ["/projects/proj-1/views/test"],
		});

		router = createRouter({
			routeTree,
			history,
			context: { queryClient },
		});

		render(<RouterProvider router={router} />);

		await waitFor(() => {
			expect(screen.getByText(/Testing Project/)).toBeInTheDocument();
		});
	});
});
