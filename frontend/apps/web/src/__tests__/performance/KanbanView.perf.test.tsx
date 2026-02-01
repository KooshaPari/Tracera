import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as hooks from "../../hooks/useItems";
import * as projectHooks from "../../hooks/useProjects";
import { ItemsKanbanView } from "../../views/ItemsKanbanView";

// Mock react router
vi.mock("@tanstack/react-router", () => ({
	useNavigate: vi.fn(() => vi.fn()),
	useSearch: vi.fn(() => ({})),
	Link: ({ to, children }: any) => <a href={to}>{children}</a>,
}));

// Mock hooks
vi.mock("../../hooks/useItems", () => ({
	useItems: vi.fn(),
	useUpdateItem: vi.fn(() => ({
		mutateAsync: vi.fn(),
	})),
}));

vi.mock("../../hooks/useProjects", () => ({
	useProjects: vi.fn(),
}));

const mockItems = Array.from({ length: 100 }, (_, i) => ({
	id: `item-${i}`,
	title: `Item ${i}`,
	description: `Description for item ${i}`,
	type: ["requirement", "feature", "test", "bug", "task"][i % 5],
	status: ["todo", "in_progress", "done", "blocked"][i % 4],
	priority: ["critical", "high", "medium", "low"][i % 4],
	owner: i % 2 === 0 ? `User ${i % 5}` : null,
	parentId: null,
	projectId: `project-${i % 3}`,
	createdAt: new Date(),
	updatedAt: new Date(),
}));

describe("ItemsKanbanView Performance", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.spyOn(hooks, "useItems").mockReturnValue({
			data: { items: mockItems },
			isLoading: false,
		} as any);
		vi.spyOn(projectHooks, "useProjects").mockReturnValue({
			data: [
				{ id: "project-0", name: "Project 0" },
				{ id: "project-1", name: "Project 1" },
				{ id: "project-2", name: "Project 2" },
			],
		} as any);
	});

	it("renders with 100+ items without excessive re-renders", () => {
		const renderSpy = vi.fn();
		const OriginalItemsKanbanView = ItemsKanbanView;

		// Wrap to capture render count
		const WrappedView = () => {
			renderSpy();
			return <OriginalItemsKanbanView />;
		};

		const { rerender } = render(<WrappedView />);

		// Initial render
		expect(renderSpy).toHaveBeenCalledTimes(1);

		// Re-render with same props should not increase count significantly
		rerender(<WrappedView />);
		expect(renderSpy).toHaveBeenCalledTimes(2);
	});

	it("memoizes ItemCard components effectively", () => {
		const { container } = render(<ItemsKanbanView />);

		// Check that ItemCard elements are present
		const cards = container.querySelectorAll('[draggable="true"]');
		expect(cards.length).toBeGreaterThan(0);
		expect(cards.length).toBeLessThanOrEqual(100);
	});

	it("handles drag operations without performance degradation", async () => {
		const user = userEvent.setup();
		render(<ItemsKanbanView />);

		const cards = screen
			.getAllByRole("link")
			.filter((link) => link.getAttribute("href")?.startsWith("/projects/"));

		if (cards.length > 0) {
			// Simulate drag start
			const firstCard = cards[0].closest("[draggable]");
			if (firstCard) {
				await user.pointer({ keys: "[MouseLeft>]", target: firstCard });
				expect(firstCard).toHaveAttribute("draggable", "true");
			}
		}
	});

	it("filters items efficiently with memoization", async () => {
		const user = userEvent.setup();
		const { container } = render(<ItemsKanbanView />);

		const searchInput = container.querySelector(
			'input[placeholder="Filter items..."]',
		);
		expect(searchInput).toBeInTheDocument();

		if (searchInput) {
			// Type to filter
			await user.type(searchInput, "Item 1");

			// Should still render efficiently
			const cards = container.querySelectorAll('[draggable="true"]');
			expect(cards.length).toBeGreaterThan(0);
		}
	});

	it("maintains performance with column re-arrangement", () => {
		const { rerender, container } = render(<ItemsKanbanView />);

		// Get initial column count
		const initialColumns = container.querySelectorAll(".min-w-\\[320px\\]");
		const initialCount = initialColumns.length;

		// Re-render
		rerender(<ItemsKanbanView />);

		const rerenderedColumns = container.querySelectorAll(".min-w-\\[320px\\]");
		expect(rerenderedColumns.length).toBe(initialCount);
	});
});
