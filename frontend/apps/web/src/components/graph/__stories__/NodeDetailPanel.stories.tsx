import type { Meta, StoryObj } from "@storybook/react";
import { NodeDetailPanel } from "../NodeDetailPanel";

const meta: Meta<typeof NodeDetailPanel> = {
	title: "Components/Graph/NodeDetailPanel",
	component: NodeDetailPanel,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 300,
		},
		layout: "fullscreen",
	},
	argTypes: {
		onClose: { action: "closed" },
		isOpen: {
			control: "boolean",
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

const mockNodeData = {
	id: "node-1",
	label: "Button Component",
	type: "component",
	properties: {
		variant: "primary",
		size: "medium",
		disabled: false,
	},
	description: "A reusable button component with multiple variants",
	relatedItems: 5,
};

/**
 * Open detail panel
 */
export const Open: Story = {
	args: {
		isOpen: true,
		node: mockNodeData,
	},
};

/**
 * Closed detail panel
 */
export const Closed: Story = {
	args: {
		isOpen: false,
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		isOpen: true,
		node: mockNodeData,
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
		isOpen: true,
		node: mockNodeData,
	},
	decorators: [
		(Story) => (
			<div className="dark" data-theme="dark">
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
 * With complex node data
 */
export const ComplexNode: Story = {
	args: {
		isOpen: true,
		node: {
			...mockNodeData,
			properties: {
				variant: ["primary", "secondary", "danger"],
				size: ["small", "medium", "large"],
				state: ["default", "hover", "active", "disabled"],
				accessibility: {
					ariaLabel: "Interactive button element",
					role: "button",
					tabIndex: 0,
				},
			},
			relatedItems: 12,
		},
	},
};
