import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

let routerInstance: ReturnType<typeof createTanStackRouter> | null = null;

export function createRouter() {
	if (!routerInstance) {
		routerInstance = createTanStackRouter({
			routeTree,
			defaultPreload: "intent",
		});
	}
	return routerInstance;
}

export function getRouter() {
	if (!routerInstance) {
		routerInstance = createRouter();
	}
	return routerInstance;
}

export type AppRouter = ReturnType<typeof createRouter>;
