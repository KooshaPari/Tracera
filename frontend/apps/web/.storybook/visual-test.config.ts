/**
 * Visual Regression Testing Configuration
 * Defines viewport sizes, theme variations, and interaction states for Chromatic
 */

export const VIEWPORTS = {
	desktop: {
		name: "Desktop",
		width: 1440,
		height: 900,
	},
	tablet: {
		name: "Tablet",
		width: 768,
		height: 1024,
	},
	mobile: {
		name: "Mobile",
		width: 375,
		height: 667,
	},
	widescreen: {
		name: "Widescreen",
		width: 1920,
		height: 1080,
	},
} as const;

export const THEMES = {
	light: {
		name: "Light",
		colorScheme: "light",
		query: "[data-theme='light']",
	},
	dark: {
		name: "Dark",
		colorScheme: "dark",
		query: "[data-theme='dark']",
	},
} as const;

export const INTERACTION_STATES = {
	default: "default",
	hover: "hover",
	focus: "focus",
	active: "active",
	disabled: "disabled",
	loading: "loading",
	error: "error",
	success: "success",
} as const;

/**
 * Viewport configurations for visual testing
 * Maps to Storybook viewport parameter
 */
export const CHROMATIC_VIEWPORT_CONFIG = {
	viewports: {
		desktop: {
			name: "Desktop",
			styles: {
				width: "1440px",
				height: "900px",
			},
		},
		tablet: {
			name: "Tablet",
			styles: {
				width: "768px",
				height: "1024px",
			},
		},
		mobile: {
			name: "Mobile",
			styles: {
				width: "375px",
				height: "667px",
			},
		},
		widescreen: {
			name: "Widescreen",
			styles: {
				width: "1920px",
				height: "1080px",
			},
		},
	},
};

/**
 * Chromatic-specific parameters
 * Handles visual regression detection and baseline management
 */
export const CHROMATIC_PARAMETERS = {
	chromatic: {
		modes: {
			light: {
				query: "[data-theme='light']",
				matcherUrl: "**/light",
			},
			dark: {
				query: "[data-theme='dark']",
				matcherUrl: "**/dark",
			},
		},
		delay: 300,
		pauseAnimationAtEnd: true,
		disableSnapshot: false,
	},
};

/**
 * Component-specific visual test configurations
 */
export const COMPONENT_VISUAL_CONFIGS = {
	UnifiedGraphView: {
		viewports: ["desktop", "tablet"],
		themes: ["light", "dark"],
		delay: 500,
		pauseAnimationAtEnd: true,
	},
	PerspectiveSelector: {
		viewports: ["desktop", "tablet", "mobile"],
		themes: ["light", "dark"],
		delay: 300,
	},
	GraphSearch: {
		viewports: ["desktop", "tablet", "mobile"],
		themes: ["light", "dark"],
		delay: 300,
	},
	NodeDetailPanel: {
		viewports: ["desktop", "tablet"],
		themes: ["light", "dark"],
		delay: 300,
	},
	GraphNodePill: {
		viewports: ["desktop", "mobile"],
		themes: ["light", "dark"],
		delay: 200,
	},
	ProgressDashboard: {
		viewports: ["desktop", "tablet"],
		themes: ["light", "dark"],
		delay: 400,
		pauseAnimationAtEnd: true,
	},
	TemporalNavigator: {
		viewports: ["desktop", "tablet"],
		themes: ["light", "dark"],
		delay: 300,
	},
} as const;

/**
 * Snapshots to be ignored from visual regression testing
 * Useful for non-deterministic elements (timestamps, random values)
 */
export const IGNORE_SNAPSHOT_REGIONS = [
	".timestamp",
	".random-id",
	".generated-hash",
	"[data-timestamp]",
	"[data-random]",
];
