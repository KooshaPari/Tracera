/**
 * Tests for itemsStore
 */

import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { useItemsStore } from "../../stores/itemsStore";
import { createMockItem } from "../mocks/data";

describe("itemsStore", () => {
	beforeEach(() => {
		// Reset store state
		const { clearItems } = useItemsStore.getState();
		clearItems();
	});

	describe("initial state", () => {
		it("should have correct initial values", () => {
			const { result } = renderHook(() => useItemsStore());

			expect(result.current.items.size).toBe(0);
			expect(result.current.itemsByProject.size).toBe(0);
			expect(result.current.isLoading).toBe(false);
			expect(result.current.loadingItems.size).toBe(0);
			expect(result.current.pendingCreates.size).toBe(0);
			expect(result.current.pendingUpdates.size).toBe(0);
			expect(result.current.pendingDeletes.size).toBe(0);
		});
	});

	describe("addItem", () => {
		it("should add an item to the store", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", project_id: "proj-1" });

			act(() => {
				result.current.addItem(item);
			});

			expect(result.current.items.get("item-1")).toEqual(item);
			expect(result.current.itemsByProject.get("proj-1")).toContain("item-1");
		});

		it("should not duplicate items in project index", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", project_id: "proj-1" });

			act(() => {
				result.current.addItem(item);
				result.current.addItem(item);
			});

			const projectItems = result.current.itemsByProject.get("proj-1");
			expect(projectItems?.filter((id) => id === "item-1").length).toBe(1);
		});
	});

	describe("addItems", () => {
		it("should add multiple items", () => {
			const { result } = renderHook(() => useItemsStore());
			const items = [
				createMockItem({ id: "item-1", project_id: "proj-1" }),
				createMockItem({ id: "item-2", project_id: "proj-1" }),
			];

			act(() => {
				result.current.addItems(items);
			});

			expect(result.current.items.size).toBe(2);
			expect(result.current.itemsByProject.get("proj-1")?.length).toBe(2);
		});
	});

	describe("updateItem", () => {
		it("should update an item", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", title: "Original" });

			act(() => {
				result.current.addItem(item);
				result.current.updateItem("item-1", { title: "Updated" });
			});

			expect(result.current.items.get("item-1")?.title).toBe("Updated");
		});

		it("should not update non-existent item", () => {
			const { result } = renderHook(() => useItemsStore());

			act(() => {
				result.current.updateItem("non-existent", { title: "Updated" });
			});

			expect(result.current.items.get("non-existent")).toBeUndefined();
		});
	});

	describe("removeItem", () => {
		it("should remove an item", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", project_id: "proj-1" });

			act(() => {
				result.current.addItem(item);
				result.current.removeItem("item-1");
			});

			expect(result.current.items.get("item-1")).toBeUndefined();
			expect(result.current.itemsByProject.get("proj-1")).not.toContain(
				"item-1",
			);
		});
	});

	describe("getItem", () => {
		it("should retrieve an item by id", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1" });

			act(() => {
				result.current.addItem(item);
			});

			const retrieved = result.current.getItem("item-1");
			expect(retrieved).toEqual(item);
		});
	});

	describe("getItemsByProject", () => {
		it("should retrieve items by project id", () => {
			const { result } = renderHook(() => useItemsStore());
			const items = [
				createMockItem({ id: "item-1", project_id: "proj-1" }),
				createMockItem({ id: "item-2", project_id: "proj-1" }),
				createMockItem({ id: "item-3", project_id: "proj-2" }),
			];

			act(() => {
				result.current.addItems(items);
			});

			const projectItems = result.current.getItemsByProject("proj-1");
			expect(projectItems.length).toBe(2);
			expect(projectItems.map((i) => i.id)).toContain("item-1");
			expect(projectItems.map((i) => i.id)).toContain("item-2");
		});
	});

	describe("optimistic creates", () => {
		it("should optimistically create an item", () => {
			const { result } = renderHook(() => useItemsStore());
			const data = {
				project_id: "proj-1",
				type: "feature" as any,
				title: "New Item",
			};

			act(() => {
				result.current.optimisticCreate("temp-1", data);
			});

			expect(result.current.items.get("temp-1")).toBeTruthy();
			expect(result.current.pendingCreates.get("temp-1")).toEqual(data);
		});

		it("should confirm optimistic create", () => {
			const { result } = renderHook(() => useItemsStore());
			const data = {
				project_id: "proj-1",
				type: "feature" as any,
				title: "New Item",
			};
			const realItem = createMockItem({ id: "real-1", ...data });

			act(() => {
				result.current.optimisticCreate("temp-1", data);
				result.current.confirmCreate("temp-1", realItem);
			});

			expect(result.current.items.get("temp-1")).toBeUndefined();
			expect(result.current.items.get("real-1")).toEqual(realItem);
			expect(result.current.pendingCreates.get("temp-1")).toBeUndefined();
		});

		it("should rollback optimistic create", () => {
			const { result } = renderHook(() => useItemsStore());
			const data = {
				project_id: "proj-1",
				type: "feature" as any,
				title: "New Item",
			};

			act(() => {
				result.current.optimisticCreate("temp-1", data);
				result.current.rollbackCreate("temp-1");
			});

			expect(result.current.items.get("temp-1")).toBeUndefined();
			expect(result.current.pendingCreates.get("temp-1")).toBeUndefined();
		});
	});

	describe("optimistic updates", () => {
		it("should optimistically update an item", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", title: "Original" });

			act(() => {
				result.current.addItem(item);
				result.current.optimisticUpdate("item-1", { title: "Updated" });
			});

			expect(result.current.items.get("item-1")?.title).toBe("Updated");
			expect(result.current.pendingUpdates.get("item-1")).toEqual({
				title: "Updated",
			});
		});

		it("should confirm optimistic update", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", title: "Original" });
			const updated = createMockItem({ id: "item-1", title: "Updated" });

			act(() => {
				result.current.addItem(item);
				result.current.optimisticUpdate("item-1", { title: "Updated" });
				result.current.confirmUpdate("item-1", updated);
			});

			expect(result.current.items.get("item-1")).toEqual(updated);
			expect(result.current.pendingUpdates.get("item-1")).toBeUndefined();
		});
	});

	describe("optimistic deletes", () => {
		it("should optimistically delete an item", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", project_id: "proj-1" });

			act(() => {
				result.current.addItem(item);
				result.current.optimisticDelete("item-1");
			});

			expect(result.current.items.get("item-1")).toBeUndefined();
			expect(result.current.pendingDeletes.has("item-1")).toBe(true);
		});

		it("should confirm optimistic delete", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1" });

			act(() => {
				result.current.addItem(item);
				result.current.optimisticDelete("item-1");
				result.current.confirmDelete("item-1");
			});

			expect(result.current.items.get("item-1")).toBeUndefined();
			expect(result.current.pendingDeletes.has("item-1")).toBe(false);
		});

		it("should rollback optimistic delete", () => {
			const { result } = renderHook(() => useItemsStore());
			const item = createMockItem({ id: "item-1", project_id: "proj-1" });

			act(() => {
				result.current.addItem(item);
				result.current.optimisticDelete("item-1");
				result.current.rollbackDelete("item-1", item);
			});

			expect(result.current.items.get("item-1")).toEqual(item);
			expect(result.current.pendingDeletes.has("item-1")).toBe(false);
		});
	});

	describe("loading states", () => {
		it("should set global loading state", () => {
			const { result } = renderHook(() => useItemsStore());

			act(() => {
				result.current.setLoading(true);
			});

			expect(result.current.isLoading).toBe(true);

			act(() => {
				result.current.setLoading(false);
			});

			expect(result.current.isLoading).toBe(false);
		});

		it("should set item-specific loading state", () => {
			const { result } = renderHook(() => useItemsStore());

			act(() => {
				result.current.setItemLoading("item-1", true);
			});

			expect(result.current.loadingItems.has("item-1")).toBe(true);

			act(() => {
				result.current.setItemLoading("item-1", false);
			});

			expect(result.current.loadingItems.has("item-1")).toBe(false);
		});
	});
});
