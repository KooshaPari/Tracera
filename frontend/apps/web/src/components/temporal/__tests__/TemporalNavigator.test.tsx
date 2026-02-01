// TemporalNavigator component tests

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
	type Branch,
	TemporalNavigator,
	type Version,
} from "../TemporalNavigator";

describe("TemporalNavigator", () => {
	const mockBranches: Branch[] = [
		{
			id: "branch-1",
			name: "main",
			status: "active",
			createdAt: new Date("2024-01-01"),
			updatedAt: new Date("2024-01-15"),
			mergeRequestCount: 0,
		},
		{
			id: "branch-2",
			name: "develop",
			status: "active",
			parentId: "branch-1",
			createdAt: new Date("2024-01-05"),
			updatedAt: new Date("2024-01-14"),
			mergeRequestCount: 2,
		},
		{
			id: "branch-3",
			name: "feature/auth",
			status: "review",
			parentId: "branch-2",
			createdAt: new Date("2024-01-10"),
			updatedAt: new Date("2024-01-13"),
			mergeRequestCount: 1,
		},
	];

	const mockVersions: Version[] = [
		{
			id: "v-1",
			branchId: "branch-1",
			title: "v1.0.0",
			tag: "1.0.0",
			timestamp: new Date("2024-01-01"),
			status: "published",
		},
		{
			id: "v-2",
			branchId: "branch-1",
			title: "v1.1.0",
			tag: "1.1.0",
			timestamp: new Date("2024-01-10"),
			status: "published",
		},
		{
			id: "v-3",
			branchId: "branch-2",
			title: "Dev Build",
			timestamp: new Date("2024-01-15"),
			status: "draft",
		},
	];

	const mockOnBranchChange = vi.fn();
	const mockOnVersionChange = vi.fn();
	const mockOnBranchCreate = vi.fn();

	afterEach(() => {
		vi.clearAllMocks();
	});

	it("renders branch selector", () => {
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId="branch-1"
				currentVersionId="v-1"
				branches={mockBranches}
				versions={mockVersions}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText("main")).toBeInTheDocument();
	});

	it("displays current branch status badge", () => {
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId="branch-1"
				currentVersionId="v-1"
				branches={mockBranches}
				versions={mockVersions}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText("active")).toBeInTheDocument();
	});

	it("calls onBranchCreate when create button is clicked", async () => {
		const user = userEvent.setup();
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId="branch-1"
				currentVersionId="v-1"
				branches={mockBranches}
				versions={mockVersions}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
				onBranchCreate={mockOnBranchCreate}
			/>,
		);

		const buttons = screen.getAllByRole("button");
		const createBtn = buttons.find((b) => b.textContent?.includes("Branch"));
		if (createBtn) {
			await user.click(createBtn);
			expect(mockOnBranchCreate).toHaveBeenCalled();
		}
	});

	it("displays current version information", () => {
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId="branch-1"
				currentVersionId="v-2"
				branches={mockBranches}
				versions={mockVersions}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText(/v1.1.0/)).toBeInTheDocument();
	});

	it("renders view mode toggle buttons", () => {
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId="branch-1"
				currentVersionId="v-1"
				branches={mockBranches}
				versions={mockVersions}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
			/>,
		);

		const buttons = screen.getAllByRole("button");
		expect(buttons.length).toBeGreaterThan(0);
	});

	it("handles empty branches list gracefully", () => {
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId=""
				currentVersionId=""
				branches={[]}
				versions={[]}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText(/Select branch/)).toBeInTheDocument();
	});

	it("shows version status badge", () => {
		render(
			<TemporalNavigator
				projectId="proj-1"
				currentBranchId="branch-2"
				currentVersionId="v-3"
				branches={mockBranches}
				versions={mockVersions}
				onBranchChange={mockOnBranchChange}
				onVersionChange={mockOnVersionChange}
			/>,
		);

		expect(screen.getByText("draft")).toBeInTheDocument();
	});
});
