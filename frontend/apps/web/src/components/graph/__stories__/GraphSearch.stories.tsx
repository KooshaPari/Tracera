import type { Meta, StoryObj } from "@storybook/react";
import { GraphSearch } from "../GraphSearch";

const meta: Meta<typeof GraphSearch> = {
	title: "Components/Graph/GraphSearch",
	component: GraphSearch,
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
		onSearch: { action: "search performed" },
		onHighlight: { action: "highlight" },
		compact: { control: "boolean" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default graph search component
 */
export const Default: Story = {
	args: {
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: false,
	},
};

/**
 * With search query
 */
export const WithQuery: Story = {
	args: {
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: false,
	},
	play: async ({ canvasElement }) => {
		const input = canvasElement.querySelector("input");
		if (input) {
			input.value = "button";
			input.dispatchEvent(new Event("input", { bubbles: true }));
		}
	},
};

/**
 * Compact search
 */
export const Compact: Story = {
	args: {
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: true,
	},
};

/**
 * On tablet view
 */
export const Tablet: Story = {
	args: {
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: false,
	},
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

/**
 * On mobile view
 */
export const Mobile: Story = {
	args: {
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: false,
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
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: false,
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
 * With focus state
 */
export const Focused: Story = {
	args: {
		items: [],
		onSearch: () => {},
		onHighlight: () => {},
		compact: false,
	},
	play: async ({ canvasElement }) => {
		const input = canvasElement.querySelector("input");
		if (input) {
			(input as HTMLInputElement).focus();
		}
	},
};
