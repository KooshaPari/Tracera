import type { Plugin } from "vite";
import { loadEnv } from "vite";

export function loadEnvPlugin(): Plugin {
	return {
		name: "tanstack-start-core:load-env",
		enforce: "pre",
		configResolved(config) {
			Object.assign(process.env, loadEnv(config.mode, config.root, ""));
		},
	};
}
