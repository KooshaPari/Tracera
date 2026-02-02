import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
	stories: [
		"../src/components/**/*.stories.@(js|jsx|mjs|ts|tsx)",
		"../src/views/**/*.stories.@(js|jsx|mjs|ts|tsx)",
	],
	addons: [
		getAbsolutePath("@storybook/addon-links"),
		getAbsolutePath("@storybook/addon-docs"),
		getAbsolutePath("@chromatic-com/storybook"),
	],
	framework: {
		name: getAbsolutePath("@storybook/react-vite"),
		options: {},
	},
	core: {
		disableTelemetry: true,
	},
	docs: {
		autodocs: true,
	} as Record<string, unknown>,
};

export default config;

function getAbsolutePath(value: string): any {
	return dirname(fileURLToPath(import.meta.resolve(`${value}/package.json`)));
}
