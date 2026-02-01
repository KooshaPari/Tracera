import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useBulkSelection } from "@/hooks/useBulkSelection";

describe("useBulkSelection", () => {
	it("initializes with empty selection", () => {
		const { result } = renderHook(() => useBulkSelection());

		expect(result.current.count).toBe(0);
		expect(result.current.selectedIds).toEqual([]);
		expect(result.current.hasSelection).toBe(false);
	});

	it("toggles individual items", () => {
		const { result } = renderHook(() => useBulkSelection());

		act(() => {
			result.current.toggle("item-1");
		});

		expect(result.current.isSelected("item-1")).toBe(true);
		expect(result.current.count).toBe(1);

		act(() => {
			result.current.toggle("item-1");
		});

		expect(result.current.isSelected("item-1")).toBe(false);
		expect(result.current.count).toBe(0);
	});

	it("selects multiple items", () => {
		const { result } = renderHook(() => useBulkSelection());

		act(() => {
			result.current.toggle("item-1");
			result.current.toggle("item-2");
			result.current.toggle("item-3");
		});

		expect(result.current.count).toBe(3);
		expect(result.current.selectedIds).toContain("item-1");
		expect(result.current.selectedIds).toContain("item-2");
		expect(result.current.selectedIds).toContain("item-3");
		expect(result.current.hasSelection).toBe(true);
	});

	it("selects all items at once", () => {
		const { result } = renderHook(() => useBulkSelection());

		const items = ["item-1", "item-2", "item-3"];

		act(() => {
			result.current.selectAll(items);
		});

		expect(result.current.count).toBe(3);
		expect(result.current.selectedIds).toEqual(expect.arrayContaining(items));
	});

	it("deselects all items", () => {
		const { result } = renderHook(() => useBulkSelection());

		act(() => {
			result.current.selectAll(["item-1", "item-2", "item-3"]);
		});

		expect(result.current.count).toBe(3);

		act(() => {
			result.current.deselectAll();
		});

		expect(result.current.count).toBe(0);
		expect(result.current.selectedIds).toEqual([]);
		expect(result.current.hasSelection).toBe(false);
	});

	it("clears selection", () => {
		const { result } = renderHook(() => useBulkSelection());

		act(() => {
			result.current.selectAll(["item-1", "item-2"]);
		});

		act(() => {
			result.current.clear();
		});

		expect(result.current.count).toBe(0);
		expect(result.current.hasSelection).toBe(false);
	});

	it("returns selected set in correct format", () => {
		const { result } = renderHook(() => useBulkSelection());

		act(() => {
			result.current.selectAll(["item-1", "item-2"]);
		});

		expect(result.current.selected instanceof Set).toBe(true);
		expect(result.current.selected.has("item-1")).toBe(true);
		expect(result.current.selected.has("item-2")).toBe(true);
	});

	it("returns selectedIds as array", () => {
		const { result } = renderHook(() => useBulkSelection());

		act(() => {
			result.current.selectAll(["item-1", "item-2", "item-3"]);
		});

		const ids = result.current.selectedIds;
		expect(Array.isArray(ids)).toBe(true);
		expect(ids.length).toBe(3);
	});

	it("tracks selection state correctly across operations", () => {
		const { result } = renderHook(() => useBulkSelection());

		// Start empty
		expect(result.current.hasSelection).toBe(false);

		// Add one item
		act(() => {
			result.current.toggle("item-1");
		});
		expect(result.current.hasSelection).toBe(true);
		expect(result.current.count).toBe(1);

		// Add more items
		act(() => {
			result.current.selectAll(["item-1", "item-2", "item-3"]);
		});
		expect(result.current.count).toBe(3);

		// Remove one
		act(() => {
			result.current.toggle("item-1");
		});
		expect(result.current.count).toBe(2);
		expect(result.current.isSelected("item-1")).toBe(false);
		expect(result.current.isSelected("item-2")).toBe(true);

		// Clear all
		act(() => {
			result.current.deselectAll();
		});
		expect(result.current.hasSelection).toBe(false);
		expect(result.current.count).toBe(0);
	});
});
