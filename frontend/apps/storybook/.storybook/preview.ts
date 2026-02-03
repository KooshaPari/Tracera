import type { Preview } from "@storybook/react";
import { themes } from "@storybook/theming";

const preview: Preview = {
	parameters: {
		a11y: {
			config: {
				rules: [
					{ id: "color-contrast", enabled: true },
					{ id: "label", enabled: true },
				],
			},
		},
		actions: { argTypesRegex: "^on[A-Z].*" },
		backgrounds: {
			default: "light",
			values: [
				{ name: "light", value: "#ffffff" },
				{ name: "dark", value: "#1a1a1a" },
			],
		},
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i,
			},
			expanded: true,
			sort: "requiredFirst",
		},
		docs: {
			theme: themes.light,
		},
	},
	tags: ["autodocs"],
};

export default preview;
