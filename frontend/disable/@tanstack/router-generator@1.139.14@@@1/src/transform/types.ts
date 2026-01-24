import type { Config } from "../config";
import type { ImportDeclaration, RouteNode } from "../types";

export interface TransformOptions {
	source: string;
	ctx: TransformContext;
	node: RouteNode;
}

export type TransformResult =
	| {
			result: "no-route-export";
	  }
	| {
			result: "not-modified";
	  }
	| {
			result: "modified";
			output: string;
	  }
	| {
			result: "error";
			error?: any;
	  };

export interface TransformImportsConfig {
	banned?: Array<ImportDeclaration>;
	required?: Array<ImportDeclaration>;
}

export interface TransformContext {
	target: Config["target"];
	routeId: string;
	lazy: boolean;
	verboseFileRoutes: boolean;
	preferredQuote?: '"' | "'";
}
