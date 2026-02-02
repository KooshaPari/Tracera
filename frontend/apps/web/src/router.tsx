import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

type RouterInstance = ReturnType<typeof createTanStackRouter>;

let routerInstance: RouterInstance | undefined;

export function createRouter(): RouterInstance {
	if (!routerInstance) {
		routerInstance = createTanStackRouter({
			defaultPreload: "intent",
			routeTree,
		});
	}
	return routerInstance;
}

export function getRouter(): RouterInstance {
	if (!routerInstance) {
		routerInstance = createRouter();
	}
	return routerInstance;
}

export type AppRouter = ReturnType<typeof createRouter>;
