export { index, layout, physical, rootRoute, route } from "./api";
export type {
	ConfigExport,
	ConfigFn,
	ConfigFnObject,
	ConfigFnPromise,
	VirtualRouteSubtreeConfig,
} from "./defineConfig";

export { defineVirtualSubtreeConfig } from "./defineConfig";
export type {
	IndexRoute,
	LayoutRoute,
	PhysicalSubtree,
	Route,
	VirtualRootRoute,
	VirtualRouteNode,
} from "./types";
