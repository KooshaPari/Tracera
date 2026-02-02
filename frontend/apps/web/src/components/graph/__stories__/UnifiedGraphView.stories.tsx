import type { Meta, StoryObj } from "@storybook/react";
import { UnifiedGraphView } from "../UnifiedGraphView";

const meta: Meta<typeof UnifiedGraphView> = {
	title: "Components/Graph/UnifiedGraphView",
	component: UnifiedGraphView,
	tags: ["autodocs"],
	args: {
		items: [],
		links: [],
	},
	parameters: {
		layout: "fullscreen",
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 500,
			pauseAnimationAtEnd: true,
		},
		viewport: {
			defaultViewport: "desktop",
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default unified graph view with standard layout
 */
export const Default: Story = {
	args: {
		items: [],
		links: [],
	},
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
	parameters: {
		viewport: {
			defaultViewport: "desktop",
		},
	},
};

/**
 * Graph view optimized for tablet viewing
 */
export const TabletView: Story = {
	args: { items: [], links: [] },
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

/**
 * Graph view optimized for mobile devices
 */
export const MobileView: Story = {
	args: { items: [], links: [] },
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
	parameters: {
		viewport: {
			defaultViewport: "mobile",
		},
	},
};

/**
 * Graph view with expanded layout for large screens
 */
export const WidescreenView: Story = {
	args: { items: [], links: [] },
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
	parameters: {
		viewport: {
			defaultViewport: "widescreen",
		},
	},
};

/**
 * Dark mode variant
 */
export const DarkMode: Story = {
	args: { items: [], links: [] },
	render: (args) => (
		<div className="w-full h-screen dark" data-theme="dark">
			<UnifiedGraphView {...args} />
		</div>
	),
	parameters: {
		chromatic: {
			modes: {
				dark: { query: "[data-theme='dark']" },
			},
		},
	},
};

/**
 * Light mode variant
 */
export const LightMode: Story = {
	args: { items: [], links: [] },
	render: (args) => (
		<div className="w-full h-screen" data-theme="light">
			<UnifiedGraphView {...args} />
		</div>
	),
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
			},
		},
	},
};
