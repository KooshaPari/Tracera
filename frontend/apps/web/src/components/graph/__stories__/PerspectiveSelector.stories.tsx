import type { Meta, StoryObj } from "@storybook/react";
import { PerspectiveSelector } from "../PerspectiveSelector";

const meta: Meta<typeof PerspectiveSelector> = {
	argTypes: {
		currentPerspective: {
			control: "select",
			options: [
				"all",
				"product",
				"business",
				"technical",
				"ui",
				"security",
				"performance",
			],
		},
		itemCounts: { control: "object" },
		onPerspectiveChange: { action: "perspective changed" },
	},
	component: PerspectiveSelector,
	parameters: {
		chromatic: {
			delay: 300,
			modes: {
				dark: { query: "[data-theme='dark']" },
				light: { query: "[data-theme='light']" },
			},
		},
	},
	tags: ["autodocs"],
	title: "Components/Graph/PerspectiveSelector",
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default perspective selector
 */
export const Default: Story = {
	args: {
		currentPerspective: "all",
		itemCounts: undefined,
		onPerspectiveChange: () => {},
	},
};

/**
 * With item counts
 */
export const WithCounts: Story = {
	args: {
		currentPerspective: "all",
		itemCounts: { all: 42, product: 12, technical: 20 },
		onPerspectiveChange: () => {},
	},
};

/**
 * Perspective selector on tablet
 */
export const Tablet: Story = {
	args: {
		currentPerspective: "all",
		itemCounts: undefined,
		onPerspectiveChange: () => {},
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
		itemCounts: undefined,
		onPerspectiveChange: () => {},
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
		itemCounts: undefined,
		onPerspectiveChange: () => {},
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
		itemCounts: undefined,
		onPerspectiveChange: () => {},
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
		itemCounts: undefined,
		onPerspectiveChange: () => {},
	},
	play: async ({ canvasElement }) => {
		const selector = canvasElement.querySelector("button");
		if (selector) {
			selector.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
		}
	},
};
