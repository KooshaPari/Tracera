import type { Meta, StoryObj } from "@storybook/react";
import { ProgressDashboard } from "../ProgressDashboard";

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
		progress: { control: { type: "range", min: 0, max: 100, step: 10 } },
		status: {
			control: "select",
			options: ["idle", "running", "completed", "error"],
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

const mockMetrics = {
	componentsAnalyzed: 150,
	linksDetected: 450,
	relationshipsFound: 280,
	dependenciesResolved: 320,
};

/**
 * Initial state
 */
export const Idle: Story = {
	args: {
		progress: 0,
		status: "idle",
		metrics: mockMetrics,
	},
};

/**
 * In progress
 */
export const Running: Story = {
	args: {
		progress: 45,
		status: "running",
		metrics: mockMetrics,
	},
};

/**
 * Near completion
 */
export const NearCompletion: Story = {
	args: {
		progress: 85,
		status: "running",
		metrics: mockMetrics,
	},
};

/**
 * Completed
 */
export const Completed: Story = {
	args: {
		progress: 100,
		status: "completed",
		metrics: mockMetrics,
	},
};

/**
 * Error state
 */
export const ErrorState: Story = {
	args: {
		progress: 35,
		status: "error",
		metrics: mockMetrics,
		errorMessage: "Failed to analyze components. Please try again.",
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		progress: 65,
		status: "running",
		metrics: mockMetrics,
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
		progress: 75,
		status: "running",
		metrics: mockMetrics,
	},
	decorators: [
		(Story) => (
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

/**
 * With large metrics
 */
export const LargeMetrics: Story = {
	args: {
		progress: 90,
		status: "running",
		metrics: {
			componentsAnalyzed: 2500,
			linksDetected: 8500,
			relationshipsFound: 5200,
			dependenciesResolved: 6800,
		},
	},
};
