/**
 * Tests for Deployment View Route
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

describe("Deployment View Route", () => {
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

	it("renders deployment view with project data", async () => {
		const { projectsApi, itemsApi } = await import("@/api/endpoints");

		(projectsApi.get as any).mockResolvedValue({
			id: "proj-1",
			name: "Test Project",
			description: "Test description",
		});

		(itemsApi.list as any).mockResolvedValue([
			{
				id: "item-1",
				title: "Production Deployment",
				type: "deployment",
				status: "done",
			},
		]);

		history = createMemoryHistory({
			initialEntries: ["/projects/proj-1/views/deployment"],
		});

		router = createRouter({
			routeTree,
			history,
			context: { queryClient },
		});

		render(<RouterProvider router={router} />);

		await waitFor(() => {
			expect(screen.getByText(/Deployment/i)).toBeInTheDocument();
		});
	});
});
