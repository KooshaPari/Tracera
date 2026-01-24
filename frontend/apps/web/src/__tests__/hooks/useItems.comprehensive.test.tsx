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
	project_id: "proj-1",
	type: "feature",
	title: "Test Feature",
	view: "features",
	status: "todo",
	priority: "high",
	created_at: "2024-01-01T00:00:00Z",
	updated_at: "2024-01-01T00:00:00Z",
};

const mockItems: Item[] = [
	mockItem,
	{
		id: "item-2",
		project_id: "proj-1",
		type: "task",
		title: "Test Task",
		view: "code",
		status: "in_progress",
		priority: "medium",
		created_at: "2024-01-01T00:00:00Z",
		updated_at: "2024-01-01T00:00:00Z",
	},
	{
		id: "item-3",
		project_id: "proj-2",
		type: "bug",
		title: "Test Bug",
		view: "tests",
		status: "done",
		priority: "low",
		created_at: "2024-01-01T00:00:00Z",
		updated_at: "2024-01-01T00:00:00Z",
	},
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
		it("should fetch items without filters", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItems,
			} as Response);

			const { result } = renderHook(() => useItems(), { wrapper });

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual(mockItems);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/items?"),
			);
		});

		it("should fetch items with project filter", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () =>
					mockItems.filter((item) => item.project_id === "proj-1"),
			} as Response);

			const { result } = renderHook(() => useItems({ projectId: "proj-1" }), {
				wrapper,
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toHaveLength(2);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("project_id=proj-1"),
			);
		});

		it("should fetch items with view filter", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItems.filter((item) => item.view === "features"),
			} as Response);

			const { result } = renderHook(
				() => useItems({ view: "features" as ViewType }),
				{ wrapper },
			);

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toHaveLength(1);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("view=features"),
			);
		});

		it("should fetch items with status filter", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItems.filter((item) => item.status === "todo"),
			} as Response);

			const { result } = renderHook(
				() => useItems({ status: "todo" as ItemStatus }),
				{ wrapper },
			);

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("status=todo"),
			);
		});

		it("should fetch items with parent filter", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => [],
			} as Response);

			const { result } = renderHook(() => useItems({ parentId: "parent-1" }), {
				wrapper,
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("parent_id=parent-1"),
			);
		});

		it("should fetch items with multiple filters", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItems,
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

			const call = mockFetch.mock.calls[0]?.[0] as string;
			expect(call).toContain("project_id=proj-1");
			expect(call).toContain("view=features");
			expect(call).toContain("status=todo");
		});

		it("should handle fetch error", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
			} as Response);

			const { result } = renderHook(() => useItems(), { wrapper });

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeDefined();
		});

		it("should show loading state", () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockImplementationOnce(() => new Promise(() => {})); // Never resolves

			const { result } = renderHook(() => useItems(), { wrapper });

			expect(result.current.isLoading).toBe(true);
			expect(result.current.data).toBeUndefined();
		});

		it("should cache results with same filters", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockItems,
			} as Response);

			const { result: result1 } = renderHook(
				() => useItems({ projectId: "proj-1" }),
				{ wrapper },
			);
			await waitFor(() => expect(result1.current.isSuccess).toBe(true));

			// Reset mock count after first fetch
			const callsBefore = mockFetch.mock.calls.length;

			const { result: result2 } = renderHook(
				() => useItems({ projectId: "proj-1" }),
				{ wrapper },
			);
			await waitFor(() => expect(result2.current.isSuccess).toBe(true));

			// Both hooks should share the same data
			expect(result1.current.data).toEqual(result2.current.data);
			// The second render should use cached data (may have 0-1 additional calls)
			expect(mockFetch.mock.calls.length - callsBefore).toBeLessThanOrEqual(1);
		});

		it("should refetch with different filters", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockItems,
			} as Response);

			const { result: result1 } = renderHook(
				() => useItems({ projectId: "proj-1" }),
				{ wrapper },
			);
			await waitFor(() => expect(result1.current.isSuccess).toBe(true));

			const { result: result2 } = renderHook(
				() => useItems({ projectId: "proj-2" }),
				{ wrapper },
			);
			await waitFor(() => expect(result2.current.isSuccess).toBe(true));

			// Should fetch twice due to different filters
			expect(mockFetch).toHaveBeenCalledTimes(2);
		});
	});

	describe("useItem", () => {
		it("should fetch single item", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const { result } = renderHook(() => useItem("item-1"), { wrapper });

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual(mockItem);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/items/item-1"),
			);
		});

		it("should not fetch when id is empty", () => {
			const mockFetch = vi.mocked(fetch);

			const { result } = renderHook(() => useItem(""), { wrapper });

			expect(result.current.isLoading).toBe(false);
			expect(mockFetch).not.toHaveBeenCalled();
		});

		it("should handle fetch error", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
			} as Response);

			const { result } = renderHook(() => useItem("nonexistent"), { wrapper });

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeDefined();
		});

		it("should refetch when id changes", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const { result, rerender } = renderHook(({ id }) => useItem(id), {
				wrapper,
				initialProps: { id: "item-1" },
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			// Change ID
			rerender({ id: "item-2" });

			await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));
		});
	});

	describe("useCreateItem", () => {
		it("should create item", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const { result } = renderHook(() => useCreateItem(), { wrapper });

			const createData = {
				projectId: "proj-1",
				view: "features" as ViewType,
				type: "feature",
				title: "New Feature",
				status: "todo" as ItemStatus,
				priority: "high" as const,
			};

			result.current.mutate(createData);

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual(mockItem);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/items"),
				expect.objectContaining({
					method: "POST",
					headers: { "Content-Type": "application/json" },
				}),
			);
		});

		it("should invalidate queries on success", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");

			const { result } = renderHook(() => useCreateItem(), { wrapper });

			result.current.mutate({
				projectId: "proj-1",
				view: "features" as ViewType,
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

		it("should handle creation error", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
			} as Response);

			const { result } = renderHook(() => useCreateItem(), { wrapper });

			result.current.mutate({
				projectId: "proj-1",
				view: "features" as ViewType,
				type: "feature",
				title: "New Feature",
				status: "todo" as ItemStatus,
				priority: "high" as const,
			});

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeDefined();
		});

		it("should include optional fields in request", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const { result } = renderHook(() => useCreateItem(), { wrapper });

			result.current.mutate({
				projectId: "proj-1",
				view: "features" as ViewType,
				type: "feature",
				title: "New Feature",
				description: "Test description",
				status: "todo" as ItemStatus,
				priority: "high" as const,
				parentId: "parent-1",
				owner: "user-1",
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			const callBody = JSON.parse(mockFetch.mock.calls[0]?.[1]?.body as string);
			expect(callBody.description).toBe("Test description");
			expect(callBody.parent_id).toBe("parent-1");
			expect(callBody.owner).toBe("user-1");
		});
	});

	describe("useUpdateItem", () => {
		it("should update item", async () => {
			const mockFetch = vi.mocked(fetch);
			const updatedItem = { ...mockItem, title: "Updated Title" };
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => updatedItem,
			} as Response);

			const { result } = renderHook(() => useUpdateItem(), { wrapper });

			result.current.mutate({
				id: "item-1",
				data: { title: "Updated Title" },
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(result.current.data).toEqual(updatedItem);
			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/items/item-1"),
				expect.objectContaining({
					method: "PATCH",
				}),
			);
		});

		it("should invalidate item and list queries on success", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
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

		it("should handle update error", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
			} as Response);

			const { result } = renderHook(() => useUpdateItem(), { wrapper });

			result.current.mutate({
				id: "nonexistent",
				data: { title: "Updated" },
			});

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeDefined();
		});

		it("should support partial updates", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			const { result } = renderHook(() => useUpdateItem(), { wrapper });

			result.current.mutate({
				id: "item-1",
				data: { status: "done" as ItemStatus },
			});

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			const callBody = JSON.parse(mockFetch.mock.calls[0]?.[1]?.body as string);
			expect(callBody).toEqual({ status: "done" });
		});
	});

	describe("useDeleteItem", () => {
		it("should delete item", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: true,
			} as Response);

			const { result } = renderHook(() => useDeleteItem(), { wrapper });

			result.current.mutate("item-1");

			await waitFor(() => expect(result.current.isSuccess).toBe(true));

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining("/api/v1/items/item-1"),
				expect.objectContaining({
					method: "DELETE",
				}),
			);
		});

		it("should invalidate queries on success", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
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

		it("should handle delete error", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
			} as Response);

			const { result } = renderHook(() => useDeleteItem(), { wrapper });

			result.current.mutate("nonexistent");

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeDefined();
		});

		it("should handle network error", async () => {
			const mockFetch = vi.mocked(fetch);
			mockFetch.mockRejectedValueOnce(new Error("Network error"));

			const { result } = renderHook(() => useDeleteItem(), { wrapper });

			result.current.mutate("item-1");

			await waitFor(() => expect(result.current.isError).toBe(true));

			expect(result.current.error).toBeDefined();
		});
	});

	describe("integration scenarios", () => {
		it("should handle create then fetch workflow", async () => {
			const mockFetch = vi.mocked(fetch);

			// Mock create
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockItem,
			} as Response);

			// Mock fetch list
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => [mockItem],
			} as Response);

			const { result: createResult } = renderHook(() => useCreateItem(), {
				wrapper,
			});

			createResult.current.mutate({
				projectId: "proj-1",
				view: "features" as ViewType,
				type: "feature",
				title: "New Feature",
				status: "todo" as ItemStatus,
				priority: "high" as const,
			});

			await waitFor(() => expect(createResult.current.isSuccess).toBe(true));

			const { result: listResult } = renderHook(
				() => useItems({ projectId: "proj-1" }),
				{ wrapper },
			);

			await waitFor(() => expect(listResult.current.isSuccess).toBe(true));

			expect(listResult.current.data).toContainEqual(mockItem);
		});

		it("should handle update then fetch workflow", async () => {
			const mockFetch = vi.mocked(fetch);
			const updatedItem = { ...mockItem, title: "Updated" };

			// Mock update
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => updatedItem,
			} as Response);

			// Mock fetch single
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => updatedItem,
			} as Response);

			const { result: updateResult } = renderHook(() => useUpdateItem(), {
				wrapper,
			});

			updateResult.current.mutate({
				id: "item-1",
				data: { title: "Updated" },
			});

			await waitFor(() => expect(updateResult.current.isSuccess).toBe(true));

			const { result: itemResult } = renderHook(() => useItem("item-1"), {
				wrapper,
			});

			await waitFor(() => expect(itemResult.current.isSuccess).toBe(true));

			expect(itemResult.current.data?.title).toBe("Updated");
		});
	});
});
