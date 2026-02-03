import { useEffect, useState } from "react";
import { createFileRoute, useParams } from "@tanstack/react-router";
import type { Milestone, Sprint } from "@tracertm/types";
import type { Branch, Version } from "@/components/temporal";
import { ProgressDashboard, TemporalNavigator } from "@/components/temporal";
import { logger } from "@/lib/logger";
import { requireAuth } from "@/lib/route-guards";

// Animation constants
const ANIMATION_DURATION_MS = 500;

// Mock branch data factory
const createMockBranches = (): Branch[] => [
	{
		createdAt: new Date(),
		id: "main",
		mergeRequestCount: 0,
		name: "Main",
		status: "active",
		updatedAt: new Date(),
	},
];

// Mock version data factory
const createMockVersions = (branchId: string): Version[] => [
	{
		branchId,
		id: "v1",
		status: "published",
		timestamp: new Date(),
		title: "Version 1.0",
	},
];

/**
 * Temporal Navigation View
 * Provides version/branch navigation and progress tracking
 */
export const TemporalView = () => {
	const { projectId } = useParams({ from: "/projects/$projectId/temporal" });
	const [branches, setBranches] = useState<Branch[]>([]);
	const [versions, setVersions] = useState<Version[]>([]);
	const [milestones, setMilestones] = useState<Milestone[]>([]);
	const [sprints, setSprints] = useState<Sprint[]>([]);
	const [currentBranchId, setCurrentBranchId] = useState<string>("");
	const [currentVersionId, setCurrentVersionId] = useState<string>("");
	const [isLoading, setIsLoading] = useState(true);
	const [activeTab, setActiveTab] = useState<"navigator" | "progress">(
		"navigator",
	);

	// Load temporal data
	useEffect(() => {
		const loadTemporalData = async () => {
			setIsLoading(true);
			try {
				// TODO: Replace with actual API calls
				// Const branchesData = await api.branches.list({ projectId });
				// Const versionsData = await api.versions.list({ projectId });
				// Const milestonesData = await api.milestones.list({ projectId });
				// Const sprintsData = await api.sprints.list({ projectId });

				// Mock data for now
				const mockBranches = createMockBranches();
				const firstBranchId = mockBranches[0]?.id || "";
				const mockVersions = createMockVersions(firstBranchId);

				setBranches(mockBranches);
				setVersions(mockVersions);
				setMilestones([]);
				setSprints([]);
				setCurrentBranchId(firstBranchId);
				setCurrentVersionId(mockVersions[0]?.id || "");
			} catch (error) {
				logger.error("Failed to load temporal data:", error);
			} finally {
				setIsLoading(false);
			}
		};

		loadTemporalData();
	}, [projectId]);

	const handleBranchChange = (branchId: string) => {
		setCurrentBranchId(branchId);
		// Reset version to first in branch
		const branchVersions = versions.filter((v) => v.branchId === branchId);
		const first = branchVersions[0];
		if (first) {
			setCurrentVersionId(first.id);
		}
	};

	const handleVersionChange = (versionId: string) => {
		setCurrentVersionId(versionId);
	};

	const handleMilestoneClick = (id: string) => {
		logger.info("Milestone clicked:", id);
	};

	const handleSprintClick = (id: string) => {
		logger.info("Sprint clicked:", id);
	};

	const handleNavigatorTabClick = () => {
		setActiveTab("navigator");
	};

	const handleProgressTabClick = () => {
		setActiveTab("progress");
	};

	const getNavigatorClassName = (tab: string) =>
		`px-4 py-2 font-medium transition-colors ${
			activeTab === tab
				? "border-b-2 border-primary text-primary"
				: "text-muted-foreground hover:text-foreground"
		}`;

	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Temporal Navigation
					</h1>
					<p className="text-muted-foreground">
						Version and branch management with progress tracking
					</p>
				</div>
			</div>

			<div className="flex gap-2 border-b">
				<button
					onClick={handleNavigatorTabClick}
					className={getNavigatorClassName("navigator")}
				>
					Version Navigator
				</button>
				<button
					onClick={handleProgressTabClick}
					className={getNavigatorClassName("progress")}
				>
					Progress Dashboard
				</button>
			</div>

			<div className="space-y-6">
				{activeTab === "navigator" && (
					<TemporalNavigator
						projectId={projectId}
						currentBranchId={currentBranchId}
						currentVersionId={currentVersionId}
						branches={branches}
						versions={versions}
						isLoading={isLoading}
						onBranchChange={handleBranchChange}
						onVersionChange={handleVersionChange}
					/>
				)}

				{activeTab === "progress" && (
					<ProgressDashboard
						projectId={projectId}
						milestones={milestones}
						sprints={sprints}
						isLoading={isLoading}
						onMilestoneClick={handleMilestoneClick}
						onSprintClick={handleSprintClick}
					/>
				)}
			</div>
		</div>
	);
};

export const TEMPORAL_VIEW = TemporalView;

export const Route = createFileRoute("/projects/$projectId/temporal")({
	beforeLoad: () => requireAuth(),
	component: TemporalView,
	loader: async () => ({}),
});
