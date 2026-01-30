/**
 * Comprehensive tests for useItems hooks
 * Tests all React Query hooks for items CRUD operations
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { Item, ItemStatus, ViewType } from "@tracertm/types";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	useCreateItem,
	useDeleteItem,
	useItem,
	useItems,
	useUpdateItem,
} from "../../hooks/useItems";

// Mock fetch globally
global.fetch = vi.fn();

const mockItem: Item = {
	id: "item-1",
	projectId: "proj-1",
	type: "feature",
	title: "Test Feature",
	view: "features",
	status: "todo",
	priority: "high",
	createdAt: "2024-01-01T00:00:00Z",
	updatedAt: "2024-01-01T00:00:00Z",
} as any;

const mockItems: Item[] = [
	mockItem,
	{
		id: "item-2",
		projectId: "proj-1",
		type: "task",
		title: "Test Task",
		view: "code",
		status: "in_progress",
		priority: "medium",
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	} as any,
	{
		id: "item-3",
		projectId: "proj-2",
		type: "bug",
		title: "Test Bug",
		view: "tests",
		status: "done",
		priority: "low",
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	} as any,
];

describe("useItems hooks", () => {
	let queryClient: QueryClient;

	beforeEach(() => {
		queryClient = new QueryClient({
			defaultOptions: {
				queries: {
					retry: false,
				},
				mutations: {
					retry: false,
				},
			},
		});
		vi.clearAllMocks();
	});

	const wrapper = ({ children }: { children: ReactNode }) => (
		<QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
	);

	describe("useItems", () => {
		it("should not fetch without projectId", () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => ({ items: mockItems, total: mockItems.length }),
			} as Response);

			const { result } = renderHook(() => useItems(), { wrapper });

			expect(result.current.fetchStatus).toBe("idle");
			expect(fetch).not.toHaveBeenCalled();
		});

		it("should fetch items with multiple filters", async () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => ({
					items: mockItems,
					total: mockItems.length,
				}),
			} as Response);

			const { result } = renderHook(
				() =>
					useItems({
						projectId: "proj-1",
						view: "features" as ViewType,
						status: "todo" as ItemStatus,
					}),
				{ wrapper },
			);

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			const call = (fetch as any).mock.calls[0]?.[0] as string;
			expect(call).toContain("project_id=proj-1");
			expect(call).toContain("view=features");
			expect(call).toContain("status=todo");
		});
	});

	describe("useItem", () => {
		it("should not fetch when id is empty", () => {
			const { result } = renderHook(() => useItem(""), { wrapper });

			expect(result.current.fetchStatus).toBe("idle");
			expect(fetch).not.toHaveBeenCalled();
		});
	});

	describe("useCreateItem", () => {
		it("should invalidate queries on success", async () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");

			const { result } = renderHook(() => useCreateItem(), { wrapper });

			result.current.mutate({
				projectId: "proj-1",
				view: "FEATURE" as ViewType,
				type: "feature",
				title: "New Feature",
				status: "todo" as ItemStatus,
				priority: "high" as const,
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(invalidateSpy).toHaveBeenCalledWith(
				expect.objectContaining({ queryKey: ["items"] }),
			);
		});

		it("should include optional fields in request", async () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const { result } = renderHook(() => useCreateItem(), { wrapper });

			result.current.mutate({
				projectId: "proj-1",
				view: "FEATURE" as ViewType,
				type: "feature",
				title: "New Feature",
				description: "Test description",
				status: "todo" as ItemStatus,
				priority: "high" as const,
				parentId: "parent-1",
				owner: "user-1",
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			const callBody = JSON.parse(
				(fetch as any).mock.calls[0]?.[1]?.body as string,
			);
			expect(callBody.description).toBe("Test description");
			expect(callBody.parent_id).toBe("parent-1");
			expect(callBody.owner).toBe("user-1");
		});
	});

	describe("useUpdateItem", () => {
		it("should invalidate item and list queries on success", async () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");

			const { result } = renderHook(() => useUpdateItem(), { wrapper });

			result.current.mutate({
				id: "item-1",
				data: { title: "Updated" },
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(invalidateSpy).toHaveBeenCalledWith(
				expect.objectContaining({ queryKey: ["items"] }),
			);
			expect(invalidateSpy).toHaveBeenCalledWith(
				expect.objectContaining({ queryKey: ["items", "item-1"] }),
			);
		});
	});

	describe("useDeleteItem", () => {
		it("should delete item", async () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
			} as Response);

			const { result } = renderHook(() => useDeleteItem(), { wrapper });

			result.current.mutate("item-1");

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(fetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/items/item-1"),
				expect.objectContaining({
					method: "DELETE",
				}),
			);
		});

		it("should invalidate queries on success", async () => {
			(fetch as any).mockResolvedValueOnce({
				ok: true,
			} as Response);

			const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");

			const { result } = renderHook(() => useDeleteItem(), { wrapper });

			result.current.mutate("item-1");

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(invalidateSpy).toHaveBeenCalledWith(
				expect.objectContaining({ queryKey: ["items"] }),
			);
		});
	});
});
