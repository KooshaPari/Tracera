import type { Meta, StoryObj } from "@storybook/react";
import { UnifiedGraphView } from "../UnifiedGraphView";

const meta: Meta<typeof UnifiedGraphView> = {
	args: {
		items: [],
		links: [],
	},
	component: UnifiedGraphView,
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 500,
			pauseAnimationAtEnd: true,
		},
		layout: "fullscreen",
		viewport: {
			defaultViewport: "desktop",
		},
	},
	tags: ["autodocs"],
	title: "Components/Graph/UnifiedGraphView",
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
	parameters: {
		viewport: {
			defaultViewport: "desktop",
		},
	},
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
};

/**
 * Graph view optimized for tablet viewing
 */
export const TabletView: Story = {
	args: { items: [], links: [] },
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
};

/**
 * Graph view optimized for mobile devices
 */
export const MobileView: Story = {
	args: { items: [], links: [] },
	parameters: {
		viewport: {
			defaultViewport: "mobile",
		},
	},
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
};

/**
 * Graph view with expanded layout for large screens
 */
export const WidescreenView: Story = {
	args: { items: [], links: [] },
	parameters: {
		viewport: {
			defaultViewport: "widescreen",
		},
	},
	render: (args) => (
		<div className="w-full h-screen">
			<UnifiedGraphView {...args} />
		</div>
	),
};

/**
 * Dark mode variant
 */
export const DarkMode: Story = {
	args: { items: [], links: [] },
	parameters: {
		chromatic: {
			modes: {
				dark: { query: "[data-theme='dark']" },
			},
		},
	},
	render: (args) => (
		<div className="w-full h-screen dark" data-theme="dark">
			<UnifiedGraphView {...args} />
		</div>
	),
};

/**
 * Light mode variant
 */
export const LightMode: Story = {
	args: { items: [], links: [] },
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
			},
		},
	},
	render: (args) => (
		<div className="w-full h-screen" data-theme="light">
			<UnifiedGraphView {...args} />
		</div>
	),
};
