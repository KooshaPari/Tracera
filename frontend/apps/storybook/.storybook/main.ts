import { createRequire } from "node:module";
import { dirname } from "node:path";
import type { StorybookConfig } from "@storybook/react-vite";

const require = createRequire(import.meta.url);

function getAbsolutePath(value: string): string {
	return dirname(require.resolve(`${value}/package.json`));
}

const config: StorybookConfig = {
	addons: [
		getAbsolutePath("@storybook/addon-links"),
		getAbsolutePath("@storybook/addon-docs"),
		"@storybook/addon-a11y",
		"@storybook/addon-designs",
		"@storybook/addon-coverage",
	],

	core: {
		disableTelemetry: true,
	},

	docs: {
		autodocs: "tag",
		defaultName: "Documentation",
	},

	features: {
		storyStoreV7: true,
		buildStoriesJson: true,
	},

	framework: {
		name: getAbsolutePath("@storybook/react-vite"),
		options: {
			builder: {
				viteConfigPath: undefined,
			},
		},
	},

	stories: [
		"../src/**/*.mdx",
		"../src/**/*.stories.@(js|jsx|mjs|ts|tsx)",
	],

	typescript: {
		check: true,
		reactDocgen: "react-docgen-typescript",
		reactDocgenTypescriptOptions: {
			shouldExtractLiteralValuesFromEnum: true,
			shouldRemoveUndefinedFromOptional: true,
			propFilter: (prop) => {
				if (prop.parent) {
					return !prop.parent.fileName.includes("node_modules");
				}
				return true;
			},
		},
	},
};

export default config;
