// BranchExplorer Storybook stories
import type { Meta, StoryObj } from "@storybook/react";
import { BranchExplorer } from "../BranchExplorer";
import type { Branch } from "../TemporalNavigator";

const meta = {
	title: "Temporal/BranchExplorer",
	component: BranchExplorer,
	parameters: {
		layout: "centered",
	},
	tags: ["autodocs"],
} satisfies Meta<typeof BranchExplorer>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockBranches: Branch[] = [
	{
		id: "main",
		name: "main",
		description: "Production branch",
		status: "active",
		createdAt: new Date("2024-01-01"),
		updatedAt: new Date("2024-01-20"),
		mergeRequestCount: 3,
	},
	{
		id: "develop",
		name: "develop",
		description: "Development branch",
		status: "active",
		parentId: "main",
		createdAt: new Date("2024-01-05"),
		updatedAt: new Date("2024-01-19"),
		mergeRequestCount: 5,
	},
	{
		id: "feature-auth",
		name: "feature/authentication",
		status: "review",
		parentId: "develop",
		createdAt: new Date("2024-01-10"),
		updatedAt: new Date("2024-01-15"),
		mergeRequestCount: 1,
	},
	{
		id: "feature-db",
		name: "feature/database",
		status: "review",
		parentId: "develop",
		createdAt: new Date("2024-01-08"),
		updatedAt: new Date("2024-01-18"),
		mergeRequestCount: 2,
	},
	{
		id: "hotfix-security",
		name: "hotfix/security-patch",
		status: "merged",
		parentId: "main",
		createdAt: new Date("2024-01-12"),
		updatedAt: new Date("2024-01-14"),
		mergeRequestCount: 0,
	},
	{
		id: "old-feature",
		name: "old-feature/deprecated",
		status: "abandoned",
		parentId: "develop",
		createdAt: new Date("2023-12-01"),
		updatedAt: new Date("2024-01-01"),
		mergeRequestCount: 0,
	},
];

export const Default: Story = {
	args: {
		projectId: "proj-123",
		branches: mockBranches,
		currentBranchId: "main",
		onBranchChange: (branchId) => logger.info("Branch changed to:", branchId),
	},
};

export const WithActions: Story = {
	args: {
		...Default.args,
		onBranchCreate: () => logger.info("Create branch requested"),
		onMergeRequest: (source, target) =>
			logger.info(`Merge ${source} into ${target}`),
	},
};

export const DevelopmentSelected: Story = {
	args: {
		...Default.args,
		currentBranchId: "develop",
	},
};

export const FeatureBranchSelected: Story = {
	args: {
		...Default.args,
		currentBranchId: "feature-auth",
	},
};

export const SingleBranch: Story = {
	args: {
		...Default.args,
		branches: [mockBranches[0]],
	},
};

export const EmptyBranches: Story = {
	args: {
		...Default.args,
		branches: [],
		currentBranchId: "",
	},
};
