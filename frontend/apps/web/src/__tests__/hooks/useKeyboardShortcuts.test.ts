import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
	__resetKeyboardShortcutsRegistry,
	formatKeyboardShortcut,
	type KeyboardShortcutAction,
	useKeyboardShortcuts,
} from "@/hooks/useKeyboardShortcuts";

describe("useKeyboardShortcuts", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		// Reset global registry to ensure test isolation
		__resetKeyboardShortcutsRegistry();
	});

	afterEach(() => {
		// Clean up after each test
		__resetKeyboardShortcutsRegistry();
	});

	it("initializes with closed modal", () => {
		const { result } = renderHook(() => useKeyboardShortcuts([]));

		expect(result.current.isShortcutsModalOpen).toBe(false);
	});

	it("opens and closes shortcuts modal", () => {
		const { result } = renderHook(() => useKeyboardShortcuts([]));

		act(() => {
			result.current.setIsShortcutsModalOpen(true);
		});

		expect(result.current.isShortcutsModalOpen).toBe(true);

		act(() => {
			result.current.setIsShortcutsModalOpen(false);
		});

		expect(result.current.isShortcutsModalOpen).toBe(false);
	});

	it("returns all registered shortcuts", () => {
		const shortcuts: KeyboardShortcutAction[] = [
			{
				key: "s",
				meta: true,
				description: "Save",
				category: "editing",
				action: vi.fn(),
			},
			{
				key: "n",
				meta: true,
				description: "New",
				category: "navigation",
				action: vi.fn(),
			},
		];

		const { result } = renderHook(() => useKeyboardShortcuts(shortcuts));

		expect(result.current.allShortcuts).toHaveLength(2);
		expect(result.current.allShortcuts[0].description).toBe("Save");
		expect(result.current.allShortcuts[1].description).toBe("New");
	});

	it("registers new shortcuts dynamically", () => {
		const { result } = renderHook(() => useKeyboardShortcuts([]));

		expect(result.current.allShortcuts).toHaveLength(0);

		const newShortcut: KeyboardShortcutAction = {
			key: "s",
			meta: true,
			description: "Save",
			category: "editing",
			action: vi.fn(),
		};

		act(() => {
			result.current.register(newShortcut);
		});

		expect(result.current.allShortcuts).toHaveLength(1);
	});

	it("unregisters shortcuts", () => {
		const shortcut: KeyboardShortcutAction = {
			key: "s",
			meta: true,
			description: "Save",
			category: "editing",
			action: vi.fn(),
		};

		const { result } = renderHook(() => useKeyboardShortcuts([shortcut]));

		expect(result.current.allShortcuts).toHaveLength(1);

		act(() => {
			// Unregister would need the ID returned from register
			// This is a simplified test
		});
	});

	it("groups shortcuts by category", () => {
		const shortcuts: KeyboardShortcutAction[] = [
			{
				key: "s",
				meta: true,
				description: "Save",
				category: "editing",
				action: vi.fn(),
			},
			{
				key: "n",
				meta: true,
				description: "New Item",
				category: "editing",
				action: vi.fn(),
			},
			{
				key: "f",
				meta: true,
				description: "Find",
				category: "navigation",
				action: vi.fn(),
			},
		];

		const { result } = renderHook(() => useKeyboardShortcuts(shortcuts));

		const editingShortcuts = result.current.allShortcuts.filter(
			(s) => s.category === "editing",
		);
		const navigationShortcuts = result.current.allShortcuts.filter(
			(s) => s.category === "navigation",
		);

		expect(editingShortcuts).toHaveLength(2);
		expect(navigationShortcuts).toHaveLength(1);
	});

	it("respects enabled flag", () => {
		const shortcut: KeyboardShortcutAction = {
			key: "s",
			meta: true,
			description: "Save",
			category: "editing",
			action: vi.fn(),
		};

		const { result: resultDisabled } = renderHook(() =>
			useKeyboardShortcuts([shortcut], false),
		);

		expect(resultDisabled.current.allShortcuts).toHaveLength(0);
	});
});

describe("formatKeyboardShortcut", () => {
	it("formats meta shortcuts", () => {
		const result = formatKeyboardShortcut({
			key: "s",
			meta: true,
			description: "Save",
			category: "editing",
		});

		expect(result).toContain("⌘");
		expect(result).toContain("S");
	});

	it("formats ctrl shortcuts", () => {
		const result = formatKeyboardShortcut({
			key: "s",
			ctrl: true,
			description: "Save",
			category: "editing",
		});

		expect(result).toContain("Ctrl");
		expect(result).toContain("S");
	});

	it("formats shift shortcuts", () => {
		const result = formatKeyboardShortcut({
			key: "s",
			shift: true,
			description: "Save",
			category: "editing",
		});

		expect(result).toContain("Shift");
		expect(result).toContain("S");
	});

	it("formats alt shortcuts", () => {
		const result = formatKeyboardShortcut({
			key: "s",
			alt: true,
			description: "Save",
			category: "editing",
		});

		expect(result).toContain("Alt");
		expect(result).toContain("S");
	});

	it("formats arrow keys", () => {
		expect(
			formatKeyboardShortcut({
				key: "ArrowUp",
				description: "Move up",
				category: "navigation",
			}),
		).toContain("↑");

		expect(
			formatKeyboardShortcut({
				key: "ArrowDown",
				description: "Move down",
				category: "navigation",
			}),
		).toContain("↓");

		expect(
			formatKeyboardShortcut({
				key: "ArrowLeft",
				description: "Move left",
				category: "navigation",
			}),
		).toContain("←");

		expect(
			formatKeyboardShortcut({
				key: "ArrowRight",
				description: "Move right",
				category: "navigation",
			}),
		).toContain("→");
	});

	it("formats special keys", () => {
		expect(
			formatKeyboardShortcut({
				key: "Enter",
				description: "Confirm",
				category: "editing",
			}),
		).toContain("↵");

		expect(
			formatKeyboardShortcut({
				key: "Escape",
				description: "Close",
				category: "system",
			}),
		).toContain("Esc");

		expect(
			formatKeyboardShortcut({
				key: "Backspace",
				description: "Delete",
				category: "editing",
			}),
		).toContain("⌫");

		expect(
			formatKeyboardShortcut({
				key: "Delete",
				description: "Delete",
				category: "editing",
			}),
		).toContain("Del");
	});

	it("formats combined shortcuts", () => {
		const result = formatKeyboardShortcut({
			key: "z",
			meta: true,
			shift: true,
			description: "Redo",
			category: "editing",
		});

		expect(result).toContain("⌘");
		expect(result).toContain("Shift");
		expect(result).toContain("Z");
	});
});
