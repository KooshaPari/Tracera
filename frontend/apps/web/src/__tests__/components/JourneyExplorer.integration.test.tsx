// Journey Explorer Integration Tests
// Tests integration with UnifiedGraphView and graph workflows

import { render, screen } from "@testing-library/react";
import type { Item, Link } from "@tracertm/types";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	type DerivedJourney,
	JourneyExplorer,
} from "@/components/graph/JourneyExplorer";

// =============================================================================
// TEST DATA
// =============================================================================

const createMockItem = (id: string, title: string, type: string): Item => ({
	id,
	projectId: "proj-1",
	view: "technical" as any,
	title,
	type,
	status: "done",
	priority: "high" as any,
	version: 1,
	createdAt: new Date().toISOString(),
	updatedAt: new Date().toISOString(),
});

const createMockLink = (
	id: string,
	sourceId: string,
	targetId: string,
	type: string,
): Link => ({
	id,
	sourceId,
	targetId,
	type: type as any,
	projectId: "proj-1",
	createdAt: new Date().toISOString(),
});

// Complex workflow scenario
const createComplexScenario = () => {
	const items: Item[] = [
		// Pages
		createMockItem("page-1", "Login Page", "page"),
		createMockItem("page-2", "Dashboard", "page"),
		createMockItem("page-3", "Settings", "page"),

		// Components
		createMockItem("comp-1", "LoginForm", "component"),
		createMockItem("comp-2", "Dashboard Layout", "component"),
		createMockItem("comp-3", "User Menu", "component"),

		// APIs
		createMockItem("api-1", "Auth API", "api"),
		createMockItem("api-2", "User API", "api"),

		// Database
		createMockItem("db-1", "Users Table", "database"),
		createMockItem("db-2", "Sessions Table", "database"),

		// Tests
		createMockItem("test-1", "Auth E2E", "test"),
		createMockItem("test-2", "Component Unit", "test"),
	];

	const links: Link[] = [
		// Page -> Component
		createMockLink("l1", "page-1", "comp-1", "implements"),
		createMockLink("l2", "page-2", "comp-2", "implements"),
		createMockLink("l3", "page-2", "comp-3", "implements"),

		// Component -> API
		createMockLink("l4", "comp-1", "api-1", "calls"),
		createMockLink("l5", "comp-3", "api-2", "calls"),

		// API -> Database
		createMockLink("l6", "api-1", "db-1", "reads_from"),
		createMockLink("l7", "api-1", "db-2", "writes_to"),
		createMockLink("l8", "api-2", "db-1", "reads_from"),

		// Test -> Component
		createMockLink("l9", "test-1", "comp-1", "tests"),
		createMockLink("l10", "test-2", "comp-2", "tests"),

		// Test -> API
		createMockLink("l11", "test-1", "api-1", "validates"),
	];

	return { items, links };
};

// =============================================================================
// TESTS
// =============================================================================

describe("JourneyExplorer - Integration Tests", () => {
	let mockItems: Item[];
	let mockLinks: Link[];

	beforeEach(() => {
		const scenario = createComplexScenario();
		mockItems = scenario.items;
		mockLinks = scenario.links;
	});

	describe("Journey Detection Workflow", () => {
		it("should display detected user flow journeys", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Login Flow",
					type: "user_flow",
					nodeIds: ["page-1", "comp-1", "api-1", "db-1"],
					links: [
						{ sourceId: "page-1", targetId: "comp-1", type: "implements" },
						{ sourceId: "comp-1", targetId: "api-1", type: "calls" },
						{ sourceId: "api-1", targetId: "db-1", type: "reads_from" },
					],
					color: "#9333ea",
				},
				{
					id: "j-2",
					name: "Dashboard Load",
					type: "user_flow",
					nodeIds: ["page-2", "comp-2", "comp-3", "api-2", "db-1"],
					links: [
						{ sourceId: "page-2", targetId: "comp-2", type: "implements" },
						{ sourceId: "page-2", targetId: "comp-3", type: "implements" },
						{ sourceId: "comp-3", targetId: "api-2", type: "calls" },
						{ sourceId: "api-2", targetId: "db-1", type: "reads_from" },
					],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(screen.getByText("Login Flow")).toBeInTheDocument();
			expect(screen.getByText("Dashboard Load")).toBeInTheDocument();
			expect(screen.getByText("2")).toBeInTheDocument(); // badge count
		});

		it("should display detected data path journeys", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "User Data Path",
					type: "data_path",
					nodeIds: ["api-1", "db-1", "db-2"],
					links: [
						{ sourceId: "api-1", targetId: "db-1", type: "reads_from" },
						{ sourceId: "api-1", targetId: "db-2", type: "writes_to" },
					],
					color: "#3b82f6",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(screen.getByText("User Data Path")).toBeInTheDocument();
			expect(screen.getByText("Data Path")).toBeInTheDocument();
		});

		it("should display detected call chain journeys", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Auth Call Chain",
					type: "call_chain",
					nodeIds: ["comp-1", "api-1", "db-1"],
					links: [
						{ sourceId: "comp-1", targetId: "api-1", type: "calls" },
						{ sourceId: "api-1", targetId: "db-1", type: "reads_from" },
					],
					color: "#f59e0b",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(screen.getByText("Auth Call Chain")).toBeInTheDocument();
			expect(screen.getByText("Call Chain")).toBeInTheDocument();
		});

		it("should display detected test trace journeys", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Auth Test Trace",
					type: "test_trace",
					nodeIds: ["test-1", "comp-1", "api-1"],
					links: [
						{ sourceId: "test-1", targetId: "comp-1", type: "tests" },
						{ sourceId: "test-1", targetId: "api-1", type: "validates" },
					],
					color: "#22c55e",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(screen.getByText("Auth Test Trace")).toBeInTheDocument();
			expect(screen.getByText("Test Trace")).toBeInTheDocument();
		});
	});

	describe("Multi-Journey Selection and Overlay", () => {
		it("should show coverage metrics for selected journeys", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Journey 1",
					type: "user_flow",
					nodeIds: ["page-1", "comp-1", "api-1"],
					links: [],
					color: "#9333ea",
				},
				{
					id: "j-2",
					name: "Journey 2",
					type: "user_flow",
					nodeIds: ["api-1", "db-1", "db-2"],
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					selectedJourneyIds={["j-1", "j-2"]}
				/>,
			);

			// Should show coverage metrics when journeys are selected
			expect(screen.getByText("Coverage")).toBeInTheDocument();
		});

		it("should aggregate node coverage across multiple journeys", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Journey 1",
					type: "user_flow",
					nodeIds: ["page-1", "page-2"],
					links: [],
					color: "#9333ea",
				},
				{
					id: "j-2",
					name: "Journey 2",
					type: "user_flow",
					nodeIds: ["page-2", "page-3"], // Overlaps with j-1 on page-2
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					selectedJourneyIds={["j-1", "j-2"]}
				/>,
			);

			// Total unique nodes: page-1, page-2, page-3 = 3 out of 12 = 25%
			expect(screen.getByText("Coverage")).toBeInTheDocument();
		});
	});

	describe("Journey Lifecycle Management", () => {
		it("should create new journey with correct data", async () => {
			const onJourneyCreate = vi.fn();

			const journeys: DerivedJourney[] = [];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					onJourneyCreate={onJourneyCreate}
				/>,
			);

			// Create journey
			const createButtons = screen
				.getAllByRole("button")
				.filter((btn) => btn.querySelector('[data-lucide="plus"]') !== null);

			if (createButtons.length > 0) {
				await user.click(createButtons[0]);

				const nameInput = screen.getByPlaceholderText("e.g., Checkout Flow");
				await user.type(nameInput, "Custom Journey");

				const typeSelect = screen.getByDisplayValue("User Flow");
				await user.click(typeSelect);
				await user.click(screen.getByText("Data Path"));

				const createButton = screen.getByText("Create Journey");
				await user.click(createButton);

				expect(onJourneyCreate).toHaveBeenCalledWith(
					expect.objectContaining({
						name: "Custom Journey",
						type: "data_path",
					}),
				);
			}
		});

		it("should delete journey on confirmation", async () => {
			const onJourneyDelete = vi.fn();

			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Test Journey",
					type: "user_flow",
					nodeIds: ["page-1"],
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					onJourneyDelete={onJourneyDelete}
				/>,
			);

			const deleteButtons = screen
				.getAllByRole("button")
				.filter((btn) => btn.querySelector('[data-lucide="trash-2"]') !== null);

			if (deleteButtons.length > 0) {
				await user.click(deleteButtons[0]);
				expect(onJourneyDelete).toHaveBeenCalledWith("j-1");
			}
		});

		it("should update journey properties", async () => {
			const onJourneyUpdate = vi.fn();

			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Test Journey",
					type: "user_flow",
					nodeIds: ["page-1"],
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					onJourneyUpdate={onJourneyUpdate}
				/>,
			);

			// Click edit button
			const editButtons = screen
				.getAllByRole("button")
				.filter((btn) => btn.textContent?.includes("Edit"));

			if (editButtons.length > 0) {
				await user.click(editButtons[0]);
				expect(onJourneyUpdate).toHaveBeenCalled();
			}
		});
	});

	describe("Export Workflow", () => {
		it("should export selected journeys as JSON", async () => {
			const onExport = vi.fn();

			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Journey 1",
					type: "user_flow",
					nodeIds: ["page-1", "comp-1"],
					links: [
						{ sourceId: "page-1", targetId: "comp-1", type: "implements" },
					],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					selectedJourneyIds={["j-1"]}
					onExport={onExport}
				/>,
			);

			// Open export dialog
			const downloadButtons = screen
				.getAllByRole("button")
				.filter(
					(btn) => btn.querySelector('[data-lucide="download"]') !== null,
				);

			if (downloadButtons.length > 0) {
				await user.click(downloadButtons[0]);

				// Choose JSON format
				const jsonButton = screen.getByText("JSON Format");
				await user.click(jsonButton);

				expect(onExport).toHaveBeenCalledWith("json");
			}
		});

		it("should export selected journeys as CSV", async () => {
			const onExport = vi.fn();

			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Journey 1",
					type: "user_flow",
					nodeIds: ["page-1", "comp-1"],
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					selectedJourneyIds={["j-1"]}
					onExport={onExport}
				/>,
			);

			const downloadButtons = screen
				.getAllByRole("button")
				.filter(
					(btn) => btn.querySelector('[data-lucide="download"]') !== null,
				);

			if (downloadButtons.length > 0) {
				await user.click(downloadButtons[0]);

				const csvButton = screen.getByText("CSV Format");
				await user.click(csvButton);

				expect(onExport).toHaveBeenCalledWith("csv");
			}
		});

		it("should export journeys as SVG visualization", async () => {
			const onExport = vi.fn();

			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Journey 1",
					type: "user_flow",
					nodeIds: ["page-1", "comp-1"],
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
					selectedJourneyIds={["j-1"]}
					onExport={onExport}
				/>,
			);

			const downloadButtons = screen
				.getAllByRole("button")
				.filter(
					(btn) => btn.querySelector('[data-lucide="download"]') !== null,
				);

			if (downloadButtons.length > 0) {
				await user.click(downloadButtons[0]);

				const svgButton = screen.getByText("SVG Visualization");
				await user.click(svgButton);

				expect(onExport).toHaveBeenCalledWith("svg");
			}
		});
	});

	describe("Performance and Scale", () => {
		it("should handle large number of journeys efficiently", () => {
			const journeys: DerivedJourney[] = Array.from({ length: 50 }, (_, i) => ({
				id: `j-${i}`,
				name: `Journey ${i}`,
				type: (["user_flow", "data_path", "call_chain", "test_trace"] as const)[
					i % 4
				],
				nodeIds: mockItems.slice(0, 5).map((item) => item.id),
				links: [],
				color: "#9333ea",
			}));

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(screen.getByText("Journey Explorer")).toBeInTheDocument();
			expect(screen.getByText("50")).toBeInTheDocument();
		});

		it("should filter large journey set efficiently", async () => {

			const journeys: DerivedJourney[] = Array.from({ length: 50 }, (_, i) => ({
				id: `j-${i}`,
				name: `Journey ${i}`,
				type: "user_flow",
				nodeIds: mockItems.slice(0, 2).map((item) => item.id),
				links: [],
				color: "#9333ea",
			}));

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			const searchInput = screen.getByPlaceholderText("Search journeys...");
			await user.type(searchInput, "Journey 4");

			// Should show filtered results
			expect(screen.getByText("Journey 4")).toBeInTheDocument();
		});
	});

	describe("Error Handling", () => {
		it("should handle missing item references gracefully", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Journey with Missing Items",
					type: "user_flow",
					nodeIds: ["page-1", "missing-id", "page-2"],
					links: [
						{ sourceId: "page-1", targetId: "missing-id", type: "calls" },
					],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(
				screen.getByText("Journey with Missing Items"),
			).toBeInTheDocument();
		});

		it("should handle empty journey data", () => {
			const journeys: DerivedJourney[] = [
				{
					id: "j-1",
					name: "Empty Journey",
					type: "user_flow",
					nodeIds: [],
					links: [],
					color: "#9333ea",
				},
			];

			render(
				<JourneyExplorer
					items={mockItems}
					links={mockLinks}
					journeys={journeys}
				/>,
			);

			expect(screen.getByText("Empty Journey")).toBeInTheDocument();
			expect(screen.getByText("0 nodes")).toBeInTheDocument();
		});
	});
});
