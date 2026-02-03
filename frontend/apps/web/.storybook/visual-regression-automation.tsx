/**
 * Visual Regression Testing Automation
 * Utilities for managing visual test snapshots and baselines
 */

import React from "react";
import type { Meta } from "@storybook/react";
import { COMPONENT_VISUAL_CONFIGS, THEMES } from "./visual-test.config";
import type { VIEWPORTS } from "./visual-test.config";

/**
 * Generates visual test parameters for a component
 * Automatically applies viewport and theme configurations
 */
type ConfigKey = keyof typeof COMPONENT_VISUAL_CONFIGS;
type ViewportKey = keyof typeof VIEWPORTS;

function getComponentConfig(
	componentName: string,
): (typeof COMPONENT_VISUAL_CONFIGS)[ConfigKey] | undefined {
	return Object.hasOwn(COMPONENT_VISUAL_CONFIGS, componentName)
		? (COMPONENT_VISUAL_CONFIGS[
				componentName as ConfigKey
			] as (typeof COMPONENT_VISUAL_CONFIGS)[ConfigKey])
		: undefined;
}

const DEFAULT_VISUAL_CONFIG = {
	delay: 300,
	themes: ["light", "dark"] as (keyof typeof THEMES)[],
	viewports: ["desktop", "tablet"] as ViewportKey[],
};

export function generateVisualTestParameters(
	componentName: string,
	config?: Partial<
		(typeof COMPONENT_VISUAL_CONFIGS)[keyof typeof COMPONENT_VISUAL_CONFIGS]
	>,
) {
	const fromMap = getComponentConfig(componentName);
	const defaultConfig = fromMap ?? DEFAULT_VISUAL_CONFIG;

	const mergedConfig = { ...defaultConfig, ...config };
	const mergedWithChromatic = mergedConfig as typeof defaultConfig & {
		pauseAnimationAtEnd?: boolean;
	};

	return {
		chromatic: {
			delay: mergedConfig.delay ?? 300,
			modes: mergedConfig.themes.reduce<Record<string, { query: string }>>(
				(acc, theme) => {
					const themeConfig = Object.prototype.hasOwnProperty.call(
						THEMES,
						theme,
					)
						? THEMES[theme as keyof typeof THEMES]
						: undefined;
					if (themeConfig != null) {
						acc[theme] = { query: themeConfig.query };
					}
					return acc;
				},
				{},
			),
			pauseAnimationAtEnd: mergedWithChromatic.pauseAnimationAtEnd ?? true,
		},
	};
}

/**
 * Creates viewport stories for all configured viewports
 * Useful for testing responsive designs
 */
export function createViewportStories<T extends Record<string, any>>(
	componentName: string,
	baseArgs: T,
	viewportsToTest?: ViewportKey[],
) {
	const config = getComponentConfig(componentName);
	const viewports: ViewportKey[] =
		viewportsToTest ??
		(config != null ? ([...config.viewports] as ViewportKey[]) : undefined) ??
		DEFAULT_VISUAL_CONFIG.viewports;

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
export function createThemeStories<T extends Record<string, any>>(
	baseArgs: T,
	themesToTest: (keyof typeof THEMES)[] = ["light", "dark"],
) {
	return Object.fromEntries(
		themesToTest.map((theme) => [
			theme.charAt(0).toUpperCase() + theme.slice(1),
			{
				args: baseArgs,
				decorators: [
					(Story: any) =>
						React.createElement(
							"div",
							{
								className: theme === "dark" ? "dark" : "",
								"data-theme": theme,
								style: { minHeight: "100vh" },
							},
							React.createElement(Story, null),
						),
				],
				parameters: {
					chromatic: {
						modes: {
							[theme]: {
								query: `[data-theme='${theme}']`,
							},
						},
					},
				},
			},
		]),
	);
}

/**
 * Creates interaction state stories (hover, focus, active, disabled)
 */
export function createInteractionStories<T extends Record<string, any>>(
	baseArgs: T,
	selector = "button",
) {
	return {
		Active: {
			args: baseArgs,
			play: ({ canvasElement }: { canvasElement: HTMLElement }) => {
				const element = canvasElement.querySelector(selector) as Element | null;
				if (element !== null && element !== undefined) {
					element.classList.add("active");
					element.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
				}
			},
		},
		Disabled: {
			args: { ...baseArgs, disabled: true },
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
		Hovered: {
			args: baseArgs,
			play: async ({ canvasElement }: any) => {
				const element = canvasElement.querySelector(selector);
				if (element) {
					element.dispatchEvent(
						new MouseEvent("mouseenter", { bubbles: true }),
					);
				}
			},
		},
	};
}

/**
 * Applies comprehensive visual test configuration to metadata
 * Combines viewport, theme, and interaction testing
 */
export function withVisualTestConfig<T extends Record<string, any>>(
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
	if (state != null && state !== "") {
		parts.push(state);
	}
	return parts.join("-").toLowerCase().replaceAll(/\s+/g, "-");
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
		if (componentName != null && componentName !== "") {
			return this.changes.get(componentName) ?? [];
		}
		return [...this.changes.entries()];
	}

	hasChanges(componentName?: string) {
		if (componentName != null && componentName !== "") {
			return (this.changes.get(componentName) ?? []).length > 0;
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
	const config = getComponentConfig(componentName);
	if (config === undefined) {
		return false;
	}

	const viewportList = [...config.viewports] as (keyof typeof VIEWPORTS)[];
	const missingViewports = requiredViewports.filter(
		(v) => !viewportList.includes(v),
	);
	const missingThemes = requiredThemes.filter(
		(t) => !config.themes.includes(t),
	);

	if (missingViewports.length > 0 || missingThemes.length > 0) {
		return false;
	}

	return true;
}

/**
 * Performance metrics for visual testing
 */
export class VisualTestMetrics {
	private componentCount = 0;
	private snapshotCount = 0;
	private startTime = Date.now();

	recordComponent(viewportCount: number, themeCount: number) {
		this.componentCount += 1;
		this.snapshotCount += viewportCount * themeCount;
	}

	getMetrics() {
		return {
			averageSnapshotsPerComponent: (
				this.snapshotCount / this.componentCount
			).toFixed(1),
			components: this.componentCount,
			duration: Date.now() - this.startTime,
			snapshots: this.snapshotCount,
		};
	}

	log() {
		const metrics = this.getMetrics();
	}
}

// Export singleton instance
export const visualTestMetrics = new VisualTestMetrics();
export const regressionTracker = new VisualRegressionTracker();
