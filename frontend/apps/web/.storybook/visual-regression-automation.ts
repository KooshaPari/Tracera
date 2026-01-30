/**
 * Visual Regression Testing Automation
 * Utilities for managing visual test snapshots and baselines
 */

import type { Meta } from "@storybook/react";
import { COMPONENT_VISUAL_CONFIGS, type VIEWPORTS, THEMES } from "./visual-test.config";

/**
 * Generates visual test parameters for a component
 * Automatically applies viewport and theme configurations
 */
export function generateVisualTestParameters(
	componentName: string,
	config?: Partial<typeof COMPONENT_VISUAL_CONFIGS[keyof typeof COMPONENT_VISUAL_CONFIGS]>,
) {
	const defaultConfig = COMPONENT_VISUAL_CONFIGS[
		componentName as keyof typeof COMPONENT_VISUAL_CONFIGS
	] || {
		viewports: ["desktop", "tablet"],
		themes: ["light", "dark"],
		delay: 300,
	};

	const mergedConfig = { ...defaultConfig, ...config };

	return {
		chromatic: {
			modes: mergedConfig.themes.reduce(
				(acc, theme) => {
					const themeConfig = THEMES[theme as keyof typeof THEMES];
					if (themeConfig) {
						acc[theme] = { query: themeConfig.query };
					}
					return acc;
				},
				{} as Record<string, { query: string }>,
			),
			delay: mergedConfig.delay || 300,
			pauseAnimationAtEnd: mergedConfig.pauseAnimationAtEnd ?? true,
		},
	};
}

/**
 * Creates viewport stories for all configured viewports
 * Useful for testing responsive designs
 */
export function createViewportStories<T extends { [key: string]: any }>(
	componentName: string,
	baseArgs: T,
	viewportsToTest?: (keyof typeof VIEWPORTS)[],
) {
	const config = COMPONENT_VISUAL_CONFIGS[
		componentName as keyof typeof COMPONENT_VISUAL_CONFIGS
	];
	const viewports = viewportsToTest || (config?.viewports as (keyof typeof VIEWPORTS)[]);

	return Object.fromEntries(
		viewports.map((viewport) => [
			`${viewport.charAt(0).toUpperCase()}${viewport.slice(1)}`,
			{
				args: baseArgs,
				parameters: {
					viewport: {
						defaultViewport: viewport,
					},
				},
			},
		]),
	);
}

/**
 * Creates theme variant stories (light and dark)
 */
export function createThemeStories<T extends { [key: string]: any }>(
	baseArgs: T,
	themesToTest: (keyof typeof THEMES)[] = ["light", "dark"],
) {
	return Object.fromEntries(
		themesToTest.map((theme) => [
			theme.charAt(0).toUpperCase() + theme.slice(1),
			{
				args: baseArgs,
				decorators: [
					(Story: any) => (
						<div
							className={theme === "dark" ? "dark" : ""}
							data-theme={theme}
							style={{ minHeight: "100vh" }}
						>
							<Story />
						</div>
					),
				],
				parameters: 
							[theme]: 
								query: `[data-theme='${theme}']`,,,,,
			},
		]),
	);
}

/**
 * Creates interaction state stories (hover, focus, active, disabled)
 */
export function createInteractionStories<T extends { [key: string]: any }>(
	baseArgs: T,
	selector: string = "button",
) {
	return {
		Hovered: {
			args: baseArgs,
			play: async ({ canvasElement }: any) => {
				const element = canvasElement.querySelector(selector);
				if (element) {
					element.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
				}
			},
		},
		Focused: {
			args: baseArgs,
			play: async ({ canvasElement }: any) => {
				const element = canvasElement.querySelector(selector);
				if (element) {
					(element as HTMLElement).focus();
				}
			},
		},
		Active: {
			args: baseArgs,
			play: async ({ canvasElement }: any) => {
				const element = canvasElement.querySelector(selector);
				if (element) {
					element.classList.add("active");
					element.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
				}
			},
		},
		Disabled: {
			args: { ...baseArgs, disabled: true },
		},
	};
}

/**
 * Applies comprehensive visual test configuration to metadata
 * Combines viewport, theme, and interaction testing
 */
export function withVisualTestConfig<T extends { [key: string]: any }>(
	meta: Meta<T>,
	componentName: string,
) {
	return {
		...meta,
		parameters: {
			...meta.parameters,
			...generateVisualTestParameters(componentName),
		},
	};
}

/**
 * Batch snapshot update helper
 * Generates consistent test names for snapshot tracking
 */
export function generateSnapshotName(
	componentName: string,
	variant: string,
	viewport: string,
	theme: string,
	state?: string,
) {
	const parts = [componentName, variant, viewport, theme];
	if (state) {
		parts.push(state);
	}
	return parts.join("-").toLowerCase().replace(/\s+/g, "-");
}

/**
 * Visual regression detection helper
 * Tracks which components have changed visually
 */
export class VisualRegressionTracker {
	private changes: Map<string, string[]> = new Map();

	recordChange(componentName: string, snapshotName: string) {
		if (!this.changes.has(componentName)) {
			this.changes.set(componentName, []);
		}
		this.changes.get(componentName)!.push(snapshotName);
	}

	getChanges(componentName?: string) {
		if (componentName) {
			return this.changes.get(componentName) || [];
		}
		return Array.from(this.changes.entries());
	}

	hasChanges(componentName?: string) {
		if (componentName) {
			return (this.changes.get(componentName) || []).length > 0;
		}
		return this.changes.size > 0;
	}

	clear() {
		this.changes.clear();
	}
}

/**
 * Snapshot validation helper
 * Ensures visual test configuration is complete
 */
export function validateComponentVisualTests(
	componentName: string,
	requiredViewports: (keyof typeof VIEWPORTS)[] = ["desktop", "tablet"],
	requiredThemes: (keyof typeof THEMES)[] = ["light", "dark"],
) {
	const config = COMPONENT_VISUAL_CONFIGS[
		componentName as keyof typeof COMPONENT_VISUAL_CONFIGS
	];

	if (!config) {
		console.warn(`No visual test configuration found for ${componentName}`);
		return false;
	}

	const missingViewports = requiredViewports.filter((v) => !config.viewports.includes(v));
	const missingThemes = requiredThemes.filter((t) => !config.themes.includes(t));

	if (missingViewports.length > 0) {
		console.warn(`${componentName} missing viewports: ${missingViewports.join(", ")}`);
	}

	if (missingThemes.length > 0) {
		console.warn(`${componentName} missing themes: ${missingThemes.join(", ")}`);
	}

	return missingViewports.length === 0 && missingThemes.length === 0;
}

/**
 * Performance metrics for visual testing
 */
export class VisualTestMetrics {
	private componentCount = 0;
	private snapshotCount = 0;
	private startTime = Date.now();

	recordComponent(viewportCount: number, themeCount: number) {
		this.componentCount++;
		this.snapshotCount += viewportCount * themeCount;
	}

	getMetrics() {
		return {
			components: this.componentCount,
			snapshots: this.snapshotCount,
			duration: Date.now() - this.startTime,
			averageSnapshotsPerComponent: (this.snapshotCount / this.componentCount).toFixed(1),
		};
	}

	log() {
		const metrics = this.getMetrics();
		console.log(`Visual Testing Metrics:`);
		console.log(`  Components: ${metrics.components}`);
		console.log(`  Total Snapshots: ${metrics.snapshots}`);
		console.log(`  Avg per Component: ${metrics.averageSnapshotsPerComponent}`);
		console.log(`  Duration: ${metrics.duration}ms`);
	}
}

// Export singleton instance
export const visualTestMetrics = new VisualTestMetrics();
export const regressionTracker = new VisualRegressionTracker();
