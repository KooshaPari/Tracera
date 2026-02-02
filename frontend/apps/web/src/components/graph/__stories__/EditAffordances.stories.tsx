import type { Meta, StoryObj } from "@storybook/react";
import { EditAffordances } from "../EditAffordances";

const meta: Meta<typeof EditAffordances> = {
	title: "Components/Graph/EditAffordances",
	component: EditAffordances,
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
		editType: {
			control: "select",
			options: ["instant", "agent_required", "manual"],
		},
		onEdit: { action: "edit clicked" },
		isEditing: { control: "boolean" },
		compact: { control: "boolean" },
		showLabel: { control: "boolean" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default edit affordances
 */
export const Default: Story = {
	args: {
		editType: "instant",
		isEditing: false,
	},
};

/**
 * Agent-required edit type
 */
export const AgentRequired: Story = {
	args: {
		editType: "agent_required",
		isEditing: false,
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		editType: "instant",
		isEditing: false,
	},
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

/**
 * On mobile
 */
export const Mobile: Story = {
	args: {
		editType: "instant",
		isEditing: false,
	},
	parameters: {
		viewport: {
			defaultViewport: "mobile",
		},
	},
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
	args: {
		editType: "instant",
		isEditing: false,
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
 * With hover state
 */
export const Hovered: Story = {
	args: {
		editType: "instant",
		isEditing: false,
	},
	play: async ({ canvasElement }) => {
		const element = canvasElement.querySelector("[role='group']");
		if (element) {
			element.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
		}
	},
};
