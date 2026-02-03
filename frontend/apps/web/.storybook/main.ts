import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
	addons: [
		getAbsolutePath("@storybook/addon-links"),
		getAbsolutePath("@storybook/addon-docs"),
		getAbsolutePath("@chromatic-com/storybook"),
	],
	core: {
		disableTelemetry: true,
	},
	docs: {
		autodocs: true,
	} as Record<string, unknown>,
	framework: {
		name: getAbsolutePath("@storybook/react-vite"),
		options: {},
	},
	stories: [
		"../src/components/**/*.stories.@(js|jsx|mjs|ts|tsx)",
		"../src/views/**/*.stories.@(js|jsx|mjs|ts|tsx)",
	],
};

export default config;

function getAbsolutePath(value: string): any {
	return dirname(fileURLToPath(import.meta.resolve(`${value}/package.json`)));
}
