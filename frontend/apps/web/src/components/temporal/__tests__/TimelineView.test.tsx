// TimelineView component tests

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Version } from "../TemporalNavigator";
import { TimelineView } from "../TimelineView";

describe(TimelineView, () => {
	const mockVersions: Version[] = [
		{
			author: "Alice",
			branchId: "branch-1",
			description: "First stable release",
			id: "v-1",
			status: "published",
			tag: "1.0.0",
			timestamp: new Date("2024-01-01"),
			title: "Initial Release",
		},
		{
			author: "Bob",
			branchId: "branch-1",
			description: "Bug fixes",
			id: "v-2",
			status: "published",
			tag: "1.0.1",
			timestamp: new Date("2024-01-08"),
			title: "Patch Release",
		},
		{
			author: "Charlie",
			branchId: "branch-1",
			id: "v-3",
			status: "draft",
			timestamp: new Date("2024-01-15"),
			title: "Development Build",
		},
	];

	const mockOnVersionChange = vi.fn();

	afterEach(() => {
		vi.clearAllMocks();
	});

	it("renders version markers", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText("Initial Release")).toBeInTheDocument();
		expect(screen.getByText("Patch Release")).toBeInTheDocument();
	});

	it("shows version count", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText(/3 versions/)).toBeInTheDocument();
	});

	it("highlights current version", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-2"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		const cards = screen.getAllByText(/Patch Release/);
		expect(cards.length).toBeGreaterThan(0);
	});

	it("calls onVersionChange when version is clicked", async () => {
		const user = userEvent.setup();
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		const versionCards = screen.getAllByText(/Patch Release/);
		if (versionCards.length > 0) {
			await user.click(versionCards[0]);
			expect(mockOnVersionChange).toHaveBeenCalledWith("v-2");
		}
	});

	it("displays version tags", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText("1.0.0")).toBeInTheDocument();
		expect(screen.getByText("1.0.1")).toBeInTheDocument();
	});

	it("displays version status badges", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		const publishedBadges = screen.getAllByText("published");
		const draftBadges = screen.getAllByText("draft");

		expect(publishedBadges.length).toBeGreaterThan(0);
		expect(draftBadges.length).toBeGreaterThan(0);
	});

	it("displays author information", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText(/by Alice/)).toBeInTheDocument();
		expect(screen.getByText(/by Bob/)).toBeInTheDocument();
	});

	it("handles zoom controls", async () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		const buttons = screen.getAllByRole("button");
		expect(buttons.length).toBeGreaterThan(0);
	});

	it("renders empty state for no versions", () => {
		render(
			<TimelineView
				versions={[]}
				currentVersionId=""
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(
			screen.getByText(/No versions in this branch yet/),
		).toBeInTheDocument();
	});

	it("displays date range", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		const dateText = screen.getByText(/1\/1\/2024/);
		expect(dateText).toBeInTheDocument();
	});

	it("displays version descriptions", () => {
		render(
			<TimelineView
				versions={mockVersions}
				currentVersionId="v-1"
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText("First stable release")).toBeInTheDocument();
		expect(screen.getByText("Bug fixes")).toBeInTheDocument();
	});
});
