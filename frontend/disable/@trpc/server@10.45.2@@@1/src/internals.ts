/**
 * These types have to be exported so users can generate their own types definitions files
 */

export type { AnyRootConfig, RootConfig } from "./core/internals/config";
export type { mergeRouters } from "./core/internals/mergeRouters";
export type {
	BuildProcedure,
	ProcedureBuilder,
} from "./core/internals/procedureBuilder";
export type { Overwrite, unsetMarker } from "./core/internals/utils";
export type { MiddlewareBuilder, MiddlewareFunction } from "./core/middleware";
export type { DefaultErrorShape } from "./error/formatter";
