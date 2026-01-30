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
		placeholder: {
			control: "text",
		},
		disabled: {
			control: "boolean",
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default graph search component
 */
export const Default: Story = {
	args: {
		placeholder: "Search components...",
		disabled: false,
	},
};

/**
 * With search query
 */
export const WithQuery: Story = {
	args: {
		placeholder: "Search components...",
		disabled: false,
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
 * Disabled search
 */
export const Disabled: Story = {
	args: {
		placeholder: "Search components...",
		disabled: true,
	},
};

/**
 * On tablet view
 */
export const Tablet: Story = {
	args: {
		placeholder: "Search components...",
		disabled: false,
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
		placeholder: "Search components...",
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
		placeholder: "Search components...",
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
 * With focus state
 */
export const Focused: Story = {
	args: {
		placeholder: "Search components...",
		disabled: false,
	},
	play: async ({ canvasElement }) => {
		const input = canvasElement.querySelector("input");
		if (input) {
			(input as HTMLInputElement).focus();
		}
	},
};
