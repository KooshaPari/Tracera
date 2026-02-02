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
		currentPerspective: {
			control: "select",
			options: ["all", "product", "business", "technical", "ui", "security", "performance"],
		},
		onPerspectiveChange: { action: "perspective changed" },
		itemCounts: { control: "object" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default perspective selector
 */
export const Default: Story = {
	args: {
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: undefined,
	},
};

/**
 * With item counts
 */
export const WithCounts: Story = {
	args: {
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: { all: 42, technical: 20, product: 12 },
	},
};

/**
 * Perspective selector on tablet
 */
export const Tablet: Story = {
	args: {
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: undefined,
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
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: undefined,
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
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: undefined,
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
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: undefined,
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
		currentPerspective: "all",
		onPerspectiveChange: () => {},
		itemCounts: undefined,
	},
	play: async ({ canvasElement }) => {
		const selector = canvasElement.querySelector("button");
		if (selector) {
			selector.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
		}
	},
};
