export type { BaseConfig, Config } from "./config";
export {
	baseConfigSchema,
	configSchema,
	getConfig,
	resolveConfigPath,
} from "./config";
export { getRouteNodes as physicalGetRouteNodes } from "./filesystem/physical/getRouteNodes";
export { rootPathId } from "./filesystem/physical/rootPathId";
export { getRouteNodes as virtualGetRouteNodes } from "./filesystem/virtual/getRouteNodes";
export type { FileEvent, FileEventType, GeneratorEvent } from "./generator";
export { Generator } from "./generator";
export type { GeneratorPlugin } from "./plugin/types";
export type {
	TransformContext,
	TransformImportsConfig,
	TransformOptions,
} from "./transform/types";
export { ensureStringArgument } from "./transform/utils";
export type {
	GetRouteNodesResult,
	GetRoutesByFileMapResult,
	GetRoutesByFileMapResultValue,
	HandleNodeAccumulator,
	ImportDeclaration,
	ImportSpecifier,
	RouteNode,
} from "./types";
export {
	capitalize,
	checkRouteFullPathUniqueness,
	cleanPath,
	determineInitialRoutePath,
	format,
	inferFullPath,
	multiSortBy,
	removeExt,
	removeLeadingSlash,
	removeTrailingSlash,
	removeUnderscores,
	replaceBackslash,
	resetRegex,
	routePathToVariable,
	trimPathLeft,
	writeIfDifferent,
} from "./utils";
