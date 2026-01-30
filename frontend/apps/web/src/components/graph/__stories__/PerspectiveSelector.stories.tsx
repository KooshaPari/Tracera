import type { Meta, StoryObj } from "@storybook/react";
import { PerspectiveSelector } from "../PerspectiveSelector";

const meta: Meta<typeof PerspectiveSelector> = {
	title: "Components/Graph/PerspectiveSelector",
	component: PerspectiveSelector,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 300,
		},
	},
	argTypes: {
		onPerspectiveChange: { action: "perspective changed" },
		disabled: {
			control: "boolean",
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default perspective selector
 */
export const Default: Story = {
	args: {
		disabled: false,
	},
};

/**
 * Disabled state
 */
export const Disabled: Story = {
	args: {
		disabled: true,
	},
};

/**
 * Perspective selector on tablet
 */
export const Tablet: Story = {
	args: {
		disabled: false,
	},
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

/**
 * Perspective selector on mobile
 */
export const Mobile: Story = {
	args: {
		disabled: false,
	},
	parameters: {
		viewport: {
			defaultViewport: "mobile",
		},
	},
};

/**
 * Dark mode variant
 */
export const DarkMode: Story = {
	args: {
		disabled: false,
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
 * With focused state
 */
export const Focused: Story = {
	args: {
		disabled: false,
	},
	play: async ({ canvasElement }) => {
		const selector = canvasElement.querySelector("button");
		if (selector) {
			(selector as HTMLButtonElement).focus();
		}
	},
};

/**
 * With hover state
 */
export const Hovered: Story = {
	args: {
		disabled: false,
	},
	play: async ({ canvasElement }) => {
		const selector = canvasElement.querySelector("button");
		if (selector) {
			selector.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
		}
	},
};
