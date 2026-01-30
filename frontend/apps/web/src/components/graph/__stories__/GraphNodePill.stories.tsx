import type { Meta, StoryObj } from "@storybook/react";
import { GraphNodePill } from "../GraphNodePill";

const meta: Meta<typeof GraphNodePill> = {
	title: "Components/Graph/GraphNodePill",
	component: GraphNodePill,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 200,
		},
	},
	argTypes: {
		onClick: { action: "clicked" },
		isSelected: { control: "boolean" },
		isHighlighted: { control: "boolean" },
		variant: {
			control: "select",
			options: ["component", "view", "route", "state", "event"],
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default node pill
 */
export const Default: Story = {
	args: {
		label: "Button Component",
		variant: "component",
		isSelected: false,
		isHighlighted: false,
	},
};

/**
 * Selected state
 */
export const Selected: Story = {
	args: {
		label: "Button Component",
		variant: "component",
		isSelected: true,
		isHighlighted: false,
	},
};

/**
 * Highlighted state
 */
export const Highlighted: Story = {
	args: {
		label: "Button Component",
		variant: "component",
		isSelected: false,
		isHighlighted: true,
	},
};

/**
 * View variant
 */
export const ViewVariant: Story = {
	args: {
		label: "Dashboard View",
		variant: "view",
		isSelected: false,
		isHighlighted: false,
	},
};

/**
 * Route variant
 */
export const RouteVariant: Story = {
	args: {
		label: "/components",
		variant: "route",
		isSelected: false,
		isHighlighted: false,
	},
};

/**
 * State variant
 */
export const StateVariant: Story = {
	args: {
		label: "Loading",
		variant: "state",
		isSelected: false,
		isHighlighted: false,
	},
};

/**
 * Event variant
 */
export const EventVariant: Story = {
	args: {
		label: "onClick",
		variant: "event",
		isSelected: false,
		isHighlighted: false,
	},
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
	args: {
		label: "Button Component",
		variant: "component",
		isSelected: false,
		isHighlighted: false,
	},
	decorators: [
		(Story) => (
			<div className="dark" data-theme="dark" style={{ padding: "20px" }}>
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
 * All variants together
 */
export const AllVariants: Story = {
	render: () => (
		<div className="flex gap-2 flex-wrap p-4">
			<GraphNodePill label="Button" variant="component" />
			<GraphNodePill label="Dashboard" variant="view" />
			<GraphNodePill label="/route" variant="route" />
			<GraphNodePill label="loading" variant="state" />
			<GraphNodePill label="onClick" variant="event" />
		</div>
	),
};
