import type { Awaitable, RegisteredRouter } from "@tanstack/router-core";
import { getStartContext } from "@tanstack/start-storage-context";
import { createIsomorphicFn } from "./createIsomorphicFn";

export const getRouterInstance: () => Awaitable<RegisteredRouter> =
	createIsomorphicFn()
		.client(() => window.__TSR_ROUTER__!)
		.server(() => getStartContext().getRouter());
