import type { Preview } from "@storybook/react";
import "../src/index.css";

const preview: Preview = {
	decorators: [
		(Story) => (
			<div className="min-h-screen bg-white dark:bg-slate-950">
				<Story />
			</div>
		),
	],
	parameters: {
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
		},
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i,
			},
		},
		layout: "fullscreen",
		viewport: {
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
			},
		},
	},
};

export default preview;
