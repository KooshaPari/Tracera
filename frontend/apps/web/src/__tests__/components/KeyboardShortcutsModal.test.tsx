import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
	type KeyboardShortcut,
	KeyboardShortcutsModal,
} from "@/components/KeyboardShortcutsModal";

describe("KeyboardShortcutsModal", () => {
	const mockOnClose = vi.fn();

	const shortcuts: KeyboardShortcut[] = [
		{
			key: "k",
			meta: true,
			description: "Open command palette",
			category: "system",
		},
		{
			key: "n",
			meta: true,
			description: "Create new item",
			category: "editing",
		},
		{
			key: "f",
			meta: true,
			description: "Search",
			category: "navigation",
		},
		{
			key: "Delete",
			description: "Bulk delete",
			category: "selection",
		},
	];

	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("does not render when closed", () => {
		const { container } = render(
			<KeyboardShortcutsModal
				isOpen={false}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		expect(container.firstChild).toBeNull();
	});

	it("renders when open", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		expect(screen.getByText(/Keyboard Shortcuts/)).toBeInTheDocument();
	});

	it("displays all shortcuts", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		expect(screen.getByText("Open command palette")).toBeInTheDocument();
		expect(screen.getByText("Create new item")).toBeInTheDocument();
		expect(screen.getByText("Search")).toBeInTheDocument();
		expect(screen.getByText("Bulk delete")).toBeInTheDocument();
	});

	it("groups shortcuts by category", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		expect(screen.getByText("System")).toBeInTheDocument();
		expect(screen.getByText("Editing")).toBeInTheDocument();
		expect(screen.getByText("Navigation")).toBeInTheDocument();
		expect(screen.getByText("Selection")).toBeInTheDocument();
	});

	it("closes modal when close button is clicked", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		const closeButton = screen.getByLabelText("Close shortcuts modal");
		fireEvent.click(closeButton);

		expect(mockOnClose).toHaveBeenCalled();
	});

	it("closes modal when clicking outside", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		const backdrop = document.querySelector(".fixed.inset-0.z-\\[101\\]");
		if (backdrop) {
			fireEvent.click(backdrop);
			expect(mockOnClose).toHaveBeenCalled();
		}
	});

	it("does not close modal when clicking content", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		const content = screen.getByText("Open command palette");
		fireEvent.click(content);

		expect(mockOnClose).not.toHaveBeenCalled();
	});

	it("closes modal on Escape key", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		fireEvent.keyDown(window, { key: "Escape" });

		expect(mockOnClose).toHaveBeenCalled();
	});

	it("displays shortcut count", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		expect(screen.getByText(/4 Shortcuts Available/)).toBeInTheDocument();
	});

	it("displays empty modal when no shortcuts provided", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={[]}
			/>,
		);

		expect(screen.getByText(/Keyboard Shortcuts/)).toBeInTheDocument();
		expect(screen.getByText(/0 Shortcuts Available/)).toBeInTheDocument();
	});

	it("shows keyboard hint in footer", () => {
		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcuts}
			/>,
		);

		expect(screen.getByText(/Press ESC or \? to close/)).toBeInTheDocument();
	});

	it("displays context when provided", () => {
		const shortcutsWithContext: KeyboardShortcut[] = [
			{
				key: "a",
				meta: true,
				description: "Select all items",
				category: "selection",
				context: "Items view",
			},
		];

		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={shortcutsWithContext}
			/>,
		);

		expect(screen.getByText(/Context: Items view/)).toBeInTheDocument();
	});

	it("handles shortcuts without modifiers", () => {
		const simpleShortcuts: KeyboardShortcut[] = [
			{
				key: "/",
				description: "Focus search",
				category: "navigation",
			},
		];

		render(
			<KeyboardShortcutsModal
				isOpen={true}
				onClose={mockOnClose}
				shortcuts={simpleShortcuts}
			/>,
		);

		expect(screen.getByText("Focus search")).toBeInTheDocument();
	});
});
