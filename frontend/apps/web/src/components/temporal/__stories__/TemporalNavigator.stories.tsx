// TemporalNavigator Storybook stories
import type { Meta, StoryObj } from "@storybook/react";
import {
	TemporalNavigator,
	type Branch,
	type Version,
} from "../TemporalNavigator";

const meta = {
	title: "Temporal/TemporalNavigator",
	component: TemporalNavigator,
	parameters: {
		layout: "centered",
	},
	tags: ["autodocs"],
} satisfies Meta<typeof TemporalNavigator>;

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
];

const mockVersions: Version[] = [
	{
		id: "v1.0.0",
		branchId: "main",
		title: "v1.0.0 - Initial Release",
		tag: "1.0.0",
		timestamp: new Date("2024-01-01"),
		author: "Alice",
		status: "published",
		description: "First stable release with core features",
	},
	{
		id: "v1.0.1",
		branchId: "main",
		title: "v1.0.1 - Bugfix",
		tag: "1.0.1",
		timestamp: new Date("2024-01-05"),
		author: "Bob",
		status: "published",
		description: "Critical security patches",
	},
	{
		id: "v1.1.0",
		branchId: "main",
		title: "v1.1.0 - New Features",
		tag: "1.1.0",
		timestamp: new Date("2024-01-12"),
		author: "Charlie",
		status: "published",
		description: "Authentication and user management",
	},
];

export const Default: Story = {
	args: {
		projectId: "proj-123",
		currentBranchId: "main",
		currentVersionId: "v1.1.0",
		branches: mockBranches,
		versions: mockVersions,
		onBranchChange: (branchId) => console.log("Branch changed to:", branchId),
		onVersionChange: (versionId) =>
			console.log("Version changed to:", versionId),
	},
};

export const WithCreateActions: Story = {
	args: {
		...Default.args,
		onBranchCreate: () => console.log("Create branch requested"),
		onMergeRequest: (source, target) =>
			console.log(`Merge ${source} into ${target}`),
	},
};

export const DevelopmentBranch: Story = {
	args: {
		...Default.args,
		currentBranchId: "develop",
	},
};
