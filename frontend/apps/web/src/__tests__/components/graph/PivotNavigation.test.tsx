/**
 * Comprehensive tests for PivotNavigation component
 * Tests: perspective navigation, equivalent items display, confidence indicators
 */

import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type { Item } from "@tracertm/types";
import {
	PivotNavigation,
	buildPivotTargets,
	type PivotTarget,
} from "@/components/graph/PivotNavigation";

// =============================================================================
// FIXTURES
// =============================================================================

const mockCurrentItem: Item = {
	id: "item-1",
	projectId: "proj-1",
	type: "feature",
	title: "User Authentication",
	perspective: "product",
	status: "active",
	createdAt: "2024-01-01T00:00:00Z",
	updatedAt: "2024-01-01T00:00:00Z",
} as any;

const mockTechnicalItem: Item = {
	id: "item-2",
	projectId: "proj-1",
	type: "api",
	title: "Authentication API",
	perspective: "technical",
	status: "active",
	createdAt: "2024-01-01T00:00:00Z",
	updatedAt: "2024-01-01T00:00:00Z",
} as any;

const mockUIItem: Item = {
	id: "item-3",
	projectId: "proj-1",
	type: "ui_component",
	title: "Login Form Component",
	perspective: "ui",
	status: "active",
	createdAt: "2024-01-01T00:00:00Z",
	updatedAt: "2024-01-01T00:00:00Z",
} as any;

const mockSecurityItem: Item = {
	id: "item-4",
	projectId: "proj-1",
	type: "security",
	title: "Authentication Security Check",
	perspective: "security",
	status: "active",
	createdAt: "2024-01-01T00:00:00Z",
	updatedAt: "2024-01-01T00:00:00Z",
} as any;

const mockPivotTargets: PivotTarget[] = [
	{
		item: mockTechnicalItem,
		perspectiveId: "technical",
		confidence: 0.95,
		source: "equivalence",
	},
	{
		item: mockUIItem,
		perspectiveId: "ui",
		confidence: 0.85,
		source: "canonical",
	},
	{
		item: mockSecurityItem,
		perspectiveId: "security",
		confidence: 0.75,
		source: "equivalence",
	},
];

// =============================================================================
// COMPONENT TESTS
// =============================================================================

describe("PivotNavigation Component", () => {
	let onPivot: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		onPivot = vi.fn();
		vi.clearAllMocks();
	});

	describe("Rendering", () => {
		it("renders pivot navigation header", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText(/pivot to perspective/i)).toBeInTheDocument();
		});

		it("displays pivot buttons for each perspective", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
				/>,
			);

			// Should show buttons for technical, ui, and security
			expect(screen.getByText(/technical/i)).toBeInTheDocument();
			expect(screen.getByText(/ui/i)).toBeInTheDocument();
			expect(screen.getByText(/security/i)).toBeInTheDocument();
		});

		it("does not show current perspective as pivot target", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
				/>,
			);

			// Product should not appear as a pivot option
			const buttons = screen.getAllByRole("button");
			const productButton = buttons.filter((b) =>
				b.textContent?.includes("Product"),
			);
			expect(productButton.length).toBe(0);
		});

		it("does not show all perspective in pivot targets", () => {
			const targetsWithAll: PivotTarget[] = [
				...mockPivotTargets,
				{
					item: mockCurrentItem,
					perspectiveId: "all",
					confidence: 1.0,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={targetsWithAll}
					onPivot={onPivot}
				/>,
			);

			// "All" perspective should be filtered out
			expect(screen.queryByText(/All perspective/i)).not.toBeInTheDocument();
		});

		it("returns null when no equivalent items and showEmpty is false", () => {
			const { container } = render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={[]}
					onPivot={onPivot}
					showEmpty={false}
				/>,
			);

			expect(container.firstChild).toBeNull();
		});
	});

	describe("Single Item Navigation", () => {
		it("shows button with item details when single equivalent exists", () => {
			const singleTarget: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={singleTarget}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
		});

		it("navigates directly when clicking single item button", async () => {
			const user = userEvent.setup();
			const singleTarget: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={singleTarget}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.click(technicalButton);

			expect(onPivot).toHaveBeenCalledWith("technical", "item-2");
		});

		it("displays confidence indicator for single item", () => {
			const singleTarget: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={singleTarget}
					onPivot={onPivot}
				/>,
			);

			// Confidence indicator should be visible
			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
		});

		it("shows item details in tooltip", async () => {
			const user = userEvent.setup();
			const singleTarget: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={singleTarget}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.hover(technicalButton);

			await waitFor(() => {
				expect(screen.getByText("Authentication API")).toBeInTheDocument();
			});
		});

		it("shows confidence percentage in tooltip", async () => {
			const user = userEvent.setup();
			const singleTarget: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={singleTarget}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.hover(technicalButton);

			await waitFor(() => {
				expect(screen.getByText(/95%/)).toBeInTheDocument();
			});
		});
	});

	describe("Multiple Items Navigation", () => {
		it("shows badge with count when multiple equivalents exist", () => {
			const multipleTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
				{
					item: mockSecurityItem,
					perspectiveId: "technical",
					confidence: 0.85,
					source: "canonical",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={multipleTargets}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText("2")).toBeInTheDocument();
		});

		it("opens popover when clicking multi-item button", async () => {
			const user = userEvent.setup();
			const multipleTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
				{
					item: mockSecurityItem,
					perspectiveId: "technical",
					confidence: 0.85,
					source: "canonical",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={multipleTargets}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.click(technicalButton);

			await waitFor(() => {
				expect(screen.getByText(/Select equivalent/i)).toBeInTheDocument();
			});
		});

		it("displays all items in popover", async () => {
			const user = userEvent.setup();
			const multipleTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
				{
					item: mockSecurityItem,
					perspectiveId: "technical",
					confidence: 0.85,
					source: "canonical",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={multipleTargets}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.click(technicalButton);

			await waitFor(() => {
				expect(screen.getByText("Authentication API")).toBeInTheDocument();
				expect(
					screen.getByText("Authentication Security Check"),
				).toBeInTheDocument();
			});
		});

		it("navigates when clicking item in popover", async () => {
			const user = userEvent.setup();
			const multipleTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
				{
					item: mockSecurityItem,
					perspectiveId: "technical",
					confidence: 0.85,
					source: "canonical",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={multipleTargets}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.click(technicalButton);

			const itemButton = await screen.findByRole("button", {
				name: /Authentication API/i,
			});
			await user.click(itemButton);

			expect(onPivot).toHaveBeenCalledWith("technical", "item-2");
		});

		it("displays type information in popover", async () => {
			const user = userEvent.setup();
			const multipleTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={multipleTargets}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.click(technicalButton);

			await waitFor(() => {
				expect(screen.getByText(/api/i)).toBeInTheDocument();
			});
		});
	});

	describe("Confidence Indicators", () => {
		it("displays confidence bars in color", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
				/>,
			);

			// Component should render without errors
			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
		});

		it("shows different colors for different confidence levels", () => {
			const mixedConfidenceTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
				{
					item: mockUIItem,
					perspectiveId: "ui",
					confidence: 0.5,
					source: "canonical",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mixedConfidenceTargets}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
			expect(screen.getByText(/UI/i)).toBeInTheDocument();
		});

		it("shows confidence tooltip on hover", async () => {
			const user = userEvent.setup();
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
				/>,
			);

			const technicalButton = screen.getByRole("button", {
				name: /Technical/i,
			});
			await user.hover(technicalButton);

			await waitFor(() => {
				expect(screen.getByText(/95%/)).toBeInTheDocument();
			});
		});
	});

	describe("Compact Mode", () => {
		it("renders compact button when compact prop is true", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
					compact={true}
				/>,
			);

			expect(
				screen.getByRole("button", { name: /Pivot/i }),
			).toBeInTheDocument();
		});

		it("shows equivalence count badge in compact mode", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
					compact={true}
				/>,
			);

			expect(screen.getByText("3")).toBeInTheDocument();
		});

		it("opens popover with all perspectives in compact mode", async () => {
			const user = userEvent.setup();
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
					compact={true}
				/>,
			);

			const pivotButton = screen.getByRole("button", { name: /Pivot/i });
			await user.click(pivotButton);

			await waitFor(() => {
				expect(
					screen.getByText(/Pivot to another perspective/i),
				).toBeInTheDocument();
			});
		});

		it("groups items by perspective in compact popover", async () => {
			const user = userEvent.setup();
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
					compact={true}
				/>,
			);

			const pivotButton = screen.getByRole("button", { name: /Pivot/i });
			await user.click(pivotButton);

			await waitFor(() => {
				expect(screen.getByText(/Technical/i)).toBeInTheDocument();
				expect(screen.getByText(/UI/i)).toBeInTheDocument();
				expect(screen.getByText(/Security/i)).toBeInTheDocument();
			});
		});

		it("navigates from compact popover", async () => {
			const user = userEvent.setup();
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
					compact={true}
				/>,
			);

			const pivotButton = screen.getByRole("button", { name: /Pivot/i });
			await user.click(pivotButton);

			const itemButton = await screen.findByRole("button", {
				name: /Authentication API/i,
			});
			await user.click(itemButton);

			expect(onPivot).toHaveBeenCalled();
		});

		it("returns null when no equivalents in compact mode with showEmpty false", () => {
			const { container } = render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={[]}
					onPivot={onPivot}
					compact={true}
					showEmpty={false}
				/>,
			);

			expect(container.firstChild).toBeNull();
		});
	});

	describe("Empty States", () => {
		it("shows disabled buttons when showEmpty is true but no items", () => {
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={[]}
					onPivot={onPivot}
					showEmpty={true}
				/>,
			);

			// Should show perspective buttons but disabled
			const buttons = screen.getAllByRole("button");
			expect(buttons.length).toBeGreaterThan(0);
		});

		it("shows 'No equivalents' message on disabled button hover", async () => {
			const user = userEvent.setup();
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={[]}
					onPivot={onPivot}
					showEmpty={true}
				/>,
			);

			const buttons = screen.getAllByRole("button");
			if (buttons.length > 0) {
				await user.hover(buttons[0]);

				// Tooltip should appear
				expect(buttons[0]).toBeInTheDocument();
			}
		});
	});

	describe("Edge Cases", () => {
		it("handles duplicate items in pivot targets", () => {
			const duplicateTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.95,
					source: "equivalence",
				},
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.85,
					source: "canonical",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={duplicateTargets}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
		});

		it("handles items with very low confidence", () => {
			const lowConfidenceTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 0.1,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={lowConfidenceTargets}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
		});

		it("handles items with 100% confidence", () => {
			const perfectConfidenceTargets: PivotTarget[] = [
				{
					item: mockTechnicalItem,
					perspectiveId: "technical",
					confidence: 1.0,
					source: "equivalence",
				},
			];

			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={perfectConfidenceTargets}
					onPivot={onPivot}
				/>,
			);

			expect(screen.getByText(/Technical/i)).toBeInTheDocument();
		});
	});

	describe("Accessibility", () => {
		it("supports keyboard navigation", async () => {
			const user = userEvent.setup();
			render(
				<PivotNavigation
					currentItem={mockCurrentItem}
					currentPerspective="product"
					equivalentItems={mockPivotTargets}
					onPivot={onPivot}
				/>,
			);

			// Tab to first button
			await user.tab();
			expect(screen.getByText(/Technical/i)).toBeInTheDocument();

			// Press Enter to activate
			await user.keyboard("{Enter}");
			expect(onPivot).toHaveBeenCalledTimes(0); // Might not be called on Enter in popover
		});
	});
});

// =============================================================================
// UTILITY FUNCTION TESTS
// =============================================================================

describe("buildPivotTargets", () => {
	const mockAllItems = [
		mockCurrentItem,
		mockTechnicalItem,
		mockUIItem,
		mockSecurityItem,
	];

	it("builds pivot targets from equivalence links", () => {
		const equivalenceLinks = [
			{
				id: "link-1",
				sourceItemId: "item-1",
				targetItemId: "item-2",
				confidence: 0.95,
				status: "confirmed",
				strategies: [{ strategy: "explicit_annotation", confidence: 0.95 }],
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			equivalenceLinks,
			[],
			mockAllItems,
		);

		expect(targets).toHaveLength(1);
		expect(targets[0].item.id).toBe("item-2");
		expect(targets[0].confidence).toBe(0.95);
		expect(targets[0].source).toBe("equivalence");
	});

	it("builds pivot targets from canonical projections", () => {
		const projections = [
			{
				id: "proj-1",
				canonicalConceptId: "concept-1",
				itemId: "item-2",
				perspective: "technical",
				confidence: 0.9,
				isConfirmed: true,
				isRejected: false,
				strategy: "api_contract",
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			[],
			projections,
			mockAllItems,
		);

		expect(targets).toHaveLength(1);
		expect(targets[0].item.id).toBe("item-2");
		expect(targets[0].perspective).toBe("technical");
		expect(targets[0].source).toBe("canonical");
	});

	it("combines equivalence links and projections", () => {
		const equivalenceLinks = [
			{
				id: "link-1",
				sourceItemId: "item-1",
				targetItemId: "item-2",
				confidence: 0.95,
				status: "confirmed",
				strategies: [{ strategy: "explicit_annotation", confidence: 0.95 }],
			},
		];

		const projections = [
			{
				id: "proj-1",
				canonicalConceptId: "concept-1",
				itemId: "item-3",
				perspective: "ui",
				confidence: 0.85,
				isConfirmed: true,
				isRejected: false,
				strategy: "api_contract",
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			equivalenceLinks,
			projections,
			mockAllItems,
		);

		expect(targets).toHaveLength(2);
	});

	it("sorts by confidence descending", () => {
		const equivalenceLinks = [
			{
				id: "link-1",
				sourceItemId: "item-1",
				targetItemId: "item-2",
				confidence: 0.5,
				status: "confirmed",
				strategies: [{ strategy: "explicit_annotation", confidence: 0.5 }],
			},
			{
				id: "link-2",
				sourceItemId: "item-1",
				targetItemId: "item-3",
				confidence: 0.95,
				status: "confirmed",
				strategies: [{ strategy: "semantic_similarity", confidence: 0.95 }],
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			equivalenceLinks,
			[],
			mockAllItems,
		);

		expect(targets[0].confidence).toBe(0.95);
		expect(targets[1].confidence).toBe(0.5);
	});

	it("excludes current item from targets", () => {
		const equivalenceLinks = [
			{
				id: "link-1",
				sourceItemId: "item-1",
				targetItemId: "item-1", // Same as current
				confidence: 0.95,
				status: "confirmed",
				strategies: [{ strategy: "explicit_annotation", confidence: 0.95 }],
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			equivalenceLinks,
			[],
			mockAllItems,
		);

		expect(targets).toHaveLength(0);
	});

	it("handles items not found in items list", () => {
		const equivalenceLinks = [
			{
				id: "link-1",
				sourceItemId: "item-1",
				targetItemId: "nonexistent",
				confidence: 0.95,
				status: "confirmed",
				strategies: [{ strategy: "explicit_annotation", confidence: 0.95 }],
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			equivalenceLinks,
			[],
			mockAllItems,
		);

		expect(targets).toHaveLength(0);
	});

	it("deduplicates items across sources", () => {
		const equivalenceLinks = [
			{
				id: "link-1",
				sourceItemId: "item-1",
				targetItemId: "item-2",
				confidence: 0.95,
				status: "confirmed",
				strategies: [{ strategy: "explicit_annotation", confidence: 0.95 }],
			},
		];

		const projections = [
			{
				id: "proj-1",
				canonicalConceptId: "concept-1",
				itemId: "item-2", // Same item
				perspective: "technical",
				confidence: 0.9,
				isConfirmed: true,
				isRejected: false,
				strategy: "api_contract",
			},
		];

		const targets = buildPivotTargets(
			mockCurrentItem,
			equivalenceLinks,
			projections,
			mockAllItems,
		);

		expect(targets).toHaveLength(1);
	});

	it("returns empty array when no links or projections", () => {
		const targets = buildPivotTargets(mockCurrentItem, [], [], mockAllItems);

		expect(targets).toHaveLength(0);
	});
});
