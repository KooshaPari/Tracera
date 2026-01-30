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
		onEdit: { action: "edit clicked" },
		onDelete: { action: "delete clicked" },
		onDuplicate: { action: "duplicate clicked" },
		isReadOnly: { control: "boolean" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default edit affordances
 */
export const Default: Story = {
	args: {
		isReadOnly: false,
	},
};

/**
 * Read-only mode (no editing available)
 */
export const ReadOnly: Story = {
	args: {
		isReadOnly: true,
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		isReadOnly: false,
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
		isReadOnly: false,
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
		isReadOnly: false,
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
		isReadOnly: false,
	},
	play: async ({ canvasElement }) => {
		const element = canvasElement.querySelector("[role='group']");
		if (element) {
			element.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
		}
	},
};
