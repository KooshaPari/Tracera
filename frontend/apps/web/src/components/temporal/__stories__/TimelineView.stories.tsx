// TimelineView Storybook stories
import type { Meta, StoryObj } from "@storybook/react";
import type { Version } from "../TemporalNavigator";
import { TimelineView } from "../TimelineView";

const meta = {
	title: "Temporal/TimelineView",
	component: TimelineView,
	parameters: {
		layout: "centered",
	},
	tags: ["autodocs"],
} satisfies Meta<typeof TimelineView>;

export default meta;
type Story = StoryObj<typeof meta>;

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
	{
		id: "v1.2.0-beta",
		branchId: "main",
		title: "v1.2.0-beta - Beta Release",
		tag: "1.2.0-beta",
		timestamp: new Date("2024-01-19"),
		author: "Alice",
		status: "draft",
		description: "Next version in development",
	},
];

export const Default: Story = {
	args: {
		versions: mockVersions,
		currentVersionId: "v1.1.0",
		onVersionChange: (versionId) =>
			logger.info("Version changed to:", versionId),
	},
};

export const SingleVersion: Story = {
	args: {
		versions: [mockVersions[0]],
		currentVersionId: "v1.0.0",
		onVersionChange: (versionId) =>
			logger.info("Version changed to:", versionId),
	},
};

export const ManyVersions: Story = {
	args: {
		versions: Array.from({ length: 20 }, (_, i) => ({
			...mockVersions[i % mockVersions.length],
			id: `v${i}`,
			title: `Version ${i}`,
			timestamp: new Date(new Date("2024-01-01").getTime() + i * 86400000),
		})),
		currentVersionId: "v10",
		onVersionChange: (versionId) =>
			logger.info("Version changed to:", versionId),
	},
};

export const EmptyTimeline: Story = {
	args: {
		versions: [],
		currentVersionId: "",
		onVersionChange: (versionId) =>
			logger.info("Version changed to:", versionId),
	},
};

export const DraftVersions: Story = {
	args: {
		versions: mockVersions.map((v) => ({
			...v,
			status: "draft" as const,
		})),
		currentVersionId: mockVersions[0].id,
		onVersionChange: (versionId) =>
			logger.info("Version changed to:", versionId),
	},
};
