/**
 * Visual Regression Testing Configuration
 * Defines viewport sizes, theme variations, and interaction states for Chromatic
 */

export const VIEWPORTS = {
	desktop: {
		height: 900,
		name: "Desktop",
		width: 1440,
	},
	mobile: {
		height: 667,
		name: "Mobile",
		width: 375,
	},
	tablet: {
		height: 1024,
		name: "Tablet",
		width: 768,
	},
	widescreen: {
		height: 1080,
		name: "Widescreen",
		width: 1920,
	},
} as const;

export const THEMES = {
	dark: {
		colorScheme: "dark",
		name: "Dark",
		query: "[data-theme='dark']",
	},
	light: {
		colorScheme: "light",
		name: "Light",
		query: "[data-theme='light']",
	},
} as const;

export const INTERACTION_STATES = {
	active: "active",
	default: "default",
	disabled: "disabled",
	error: "error",
	focus: "focus",
	hover: "hover",
	loading: "loading",
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
				height: "900px",
				width: "1440px",
			},
		},
		mobile: {
			name: "Mobile",
			styles: {
				height: "667px",
				width: "375px",
			},
		},
		tablet: {
			name: "Tablet",
			styles: {
				height: "1024px",
				width: "768px",
			},
		},
		widescreen: {
			name: "Widescreen",
			styles: {
				height: "1080px",
				width: "1920px",
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
		delay: 300,
		disableSnapshot: false,
		modes: {
			dark: {
				matcherUrl: "**/dark",
				query: "[data-theme='dark']",
			},
			light: {
				matcherUrl: "**/light",
				query: "[data-theme='light']",
			},
		},
		pauseAnimationAtEnd: true,
	},
};

/**
 * Component-specific visual test configurations
 */
export const COMPONENT_VISUAL_CONFIGS = {
	GraphNodePill: {
		delay: 200,
		themes: ["light", "dark"],
		viewports: ["desktop", "mobile"],
	},
	GraphSearch: {
		delay: 300,
		themes: ["light", "dark"],
		viewports: ["desktop", "tablet", "mobile"],
	},
	NodeDetailPanel: {
		delay: 300,
		themes: ["light", "dark"],
		viewports: ["desktop", "tablet"],
	},
	PerspectiveSelector: {
		delay: 300,
		themes: ["light", "dark"],
		viewports: ["desktop", "tablet", "mobile"],
	},
	ProgressDashboard: {
		delay: 400,
		pauseAnimationAtEnd: true,
		themes: ["light", "dark"],
		viewports: ["desktop", "tablet"],
	},
	TemporalNavigator: {
		delay: 300,
		themes: ["light", "dark"],
		viewports: ["desktop", "tablet"],
	},
	UnifiedGraphView: {
		delay: 500,
		pauseAnimationAtEnd: true,
		themes: ["light", "dark"],
		viewports: ["desktop", "tablet"],
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
