import type { Meta, StoryObj } from "@storybook/react";
import { ProgressDashboard } from "@/components/temporal/ProgressDashboard";

const meta: Meta<typeof ProgressDashboard> = {
	title: "Components/Graph/ProgressDashboard",
	component: ProgressDashboard,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 400,
			pauseAnimationAtEnd: true,
		},
		layout: "fullscreen",
	},
	argTypes: {
		projectId: { control: "text" },
		isLoading: { control: "boolean" },
		onMilestoneClick: { action: "milestoneClick" },
		onSprintClick: { action: "sprintClick" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

const mockMilestones = [
	{
		id: "m1",
		projectId: "proj-1",
		name: "v1.0 Release",
		slug: "v1-0-release",
		targetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
		status: "in_progress" as const,
		health: "green" as const,
		progress: {
			totalItems: 10,
			completedItems: 7,
			inProgressItems: 2,
			blockedItems: 0,
			notStartedItems: 1,
			percentage: 70,
		},
		itemIds: ["item-1", "item-2"],
		itemCount: 10,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
];

const mockSprints = [
	{
		id: "s1",
		projectId: "proj-1",
		name: "Sprint 1",
		slug: "sprint-1",
		startDate: new Date().toISOString(),
		endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
		durationDays: 14,
		status: "active" as const,
		health: "green" as const,
		plannedPoints: 50,
		completedPoints: 35,
		remainingPoints: 15,
		addedPoints: 0,
		removedPoints: 0,
		itemIds: [] as string[],
		itemCount: 10,
		completedItemIds: [] as string[],
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	},
];

/**
 * Default state
 */
export const Default: Story = {
	args: {
		projectId: "proj-1",
		milestones: mockMilestones,
		sprints: mockSprints,
		isLoading: false,
	},
};

/**
 * Loading state
 */
export const Loading: Story = {
	args: {
		projectId: "proj-1",
		milestones: [],
		sprints: [],
		isLoading: true,
	},
};

/**
 * Empty state
 */
export const Empty: Story = {
	args: {
		projectId: "proj-1",
		milestones: [],
		sprints: [],
		isLoading: false,
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		projectId: "proj-1",
		milestones: mockMilestones,
		sprints: mockSprints,
		isLoading: false,
	},
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
	args: {
		projectId: "proj-1",
		milestones: mockMilestones,
		sprints: mockSprints,
		isLoading: false,
	},
	decorators: [
		(Story: React.ComponentType) => (
			<div className="dark" data-theme="dark" style={{ minHeight: "100vh" }}>
				<Story />
			</div>
		),
	],
	parameters: {
		chromatic: {
			modes: {
				dark: { query: "[data-theme='dark']" },
			},
		},
	},
};
