import type { Generator } from "../generator";
import type { HandleNodeAccumulator, RouteNode } from "../types";

export interface GeneratorPlugin {
	name: string;
	init?: (opts: { generator: Generator }) => void;
	onRouteTreeChanged?: (opts: {
		routeTree: Array<RouteNode>;
		routeNodes: Array<RouteNode>;
		rootRouteNode: RouteNode;
		acc: HandleNodeAccumulator;
	}) => void;

	afterTransform?: (opts: {
		node: RouteNode;
		prevNode: RouteNode | undefined;
	}) => void;
}
