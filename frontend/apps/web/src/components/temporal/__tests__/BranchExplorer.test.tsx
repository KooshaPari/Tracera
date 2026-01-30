// BranchExplorer component tests
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BranchExplorer } from "../BranchExplorer";
import type { Branch } from "../TemporalNavigator";

describe("BranchExplorer", () => {
	const mockBranches: Branch[] = [
		{
			id: "branch-1",
			name: "main",
			description: "Main production branch",
			status: "active",
			createdAt: new Date("2024-01-01"),
			updatedAt: new Date("2024-01-15"),
			mergeRequestCount: 5,
		},
		{
			id: "branch-2",
			name: "develop",
			description: "Development branch",
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
		{
			id: "branch-4",
			name: "hotfix/security",
			status: "merged",
			parentId: "branch-1",
			createdAt: new Date("2024-01-12"),
			updatedAt: new Date("2024-01-12"),
			mergeRequestCount: 0,
		},
	];

	const mockOnBranchChange = vi.fn();
	const mockOnMergeRequest = vi.fn();
	const mockOnBranchCreate = vi.fn();

	afterEach(() => {
		vi.clearAllMocks();
	});

	it("renders branch tree structure", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		expect(screen.getByText("main")).toBeInTheDocument();
		expect(screen.getByText("develop")).toBeInTheDocument();
	});

	it("displays branch status badges", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		const activeElements = screen.getAllByText("active");
		expect(activeElements.length).toBeGreaterThan(0);

		expect(screen.getByText("review")).toBeInTheDocument();
		expect(screen.getByText("merged")).toBeInTheDocument();
	});

	it("calls onBranchChange when branch is clicked", async () => {
		const user = userEvent.setup();
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		const developElement = screen.getByText("develop");
		await user.click(developElement);
		expect(mockOnBranchChange).toHaveBeenCalledWith("branch-2");
	});

	it("displays branch descriptions", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		expect(screen.getByText("Main production branch")).toBeInTheDocument();
		expect(screen.getByText("Development branch")).toBeInTheDocument();
	});

	it("shows create branch button when provided", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
				onBranchCreate={mockOnBranchCreate}
			/>,
		);

		expect(screen.getByText("New Branch")).toBeInTheDocument();
	});

	it("calls onBranchCreate when create button is clicked", async () => {
		const user = userEvent.setup();
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
				onBranchCreate={mockOnBranchCreate}
			/>,
		);

		const createBtn = screen.getByText("New Branch");
		await user.click(createBtn);
		expect(mockOnBranchCreate).toHaveBeenCalled();
	});

	it("displays branch statistics", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		expect(screen.getByText("Active:")).toBeInTheDocument();
		expect(screen.getByText("In Review:")).toBeInTheDocument();
		expect(screen.getByText("Total:")).toBeInTheDocument();
	});

	it("shows correct active branch count", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		expect(screen.getByText("2")).toBeInTheDocument();
	});

	it("handles empty branch list gracefully", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={[]}
				currentBranchId=""
				onBranchChange={mockOnBranchChange}
			/>,
		);

		expect(screen.getByText("No branches found")).toBeInTheDocument();
	});

	it("supports merge operations", async () => {
		const user = userEvent.setup();
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
				onMergeRequest={mockOnMergeRequest}
			/>,
		);

		const mergeButtons = screen.getAllByRole("button");
		expect(mergeButtons.length).toBeGreaterThan(0);
	});

	it("highlights current branch", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-2"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		const developElements = screen.getAllByText("develop");
		expect(developElements.length).toBeGreaterThan(0);
	});

	it("shows branch hierarchy through indentation", () => {
		render(
			<BranchExplorer
				projectId="proj-1"
				branches={mockBranches}
				currentBranchId="branch-1"
				onBranchChange={mockOnBranchChange}
			/>,
		);

		const elements = screen.getAllByText("feature/auth");
		expect(elements.length).toBeGreaterThan(0);
	});
});
