export type { Register } from "@tanstack/router-core";
export type {
	DehydratedRouter,
	JsonResponse,
} from "@tanstack/router-core/ssr/client";
export { hydrate, json, mergeHeaders } from "@tanstack/router-core/ssr/client";
export {
	TSS_FORMDATA_CONTEXT,
	TSS_SERVER_FUNCTION,
	X_TSS_RAW_RESPONSE,
	X_TSS_SERIALIZED,
} from "./constants";
export {
	type ClientOnlyFn,
	createIsomorphicFn,
	type IsomorphicFn,
	type IsomorphicFnBase,
	type ServerOnlyFn,
} from "./createIsomorphicFn";
export {
	type AnyFunctionMiddleware,
	type AnyRequestMiddleware,
	type AssignAllClientContextBeforeNext,
	type AssignAllMiddleware,
	createMiddleware,
	type FunctionClientResultWithContext,
	type FunctionMiddleware,
	type FunctionMiddlewareAfterClient,
	type FunctionMiddlewareAfterMiddleware,
	type FunctionMiddlewareAfterServer,
	type FunctionMiddlewareAfterValidator,
	type FunctionMiddlewareClient,
	type FunctionMiddlewareClientFn,
	type FunctionMiddlewareClientFnOptions,
	type FunctionMiddlewareClientFnResult,
	type FunctionMiddlewareClientNextFn,
	type FunctionMiddlewareOptions,
	type FunctionMiddlewareServer,
	type FunctionMiddlewareServerFn,
	type FunctionMiddlewareServerFnOptions,
	type FunctionMiddlewareServerFnResult,
	type FunctionMiddlewareServerNextFn,
	type FunctionMiddlewareValidator,
	type FunctionMiddlewareWithTypes,
	type FunctionServerResultWithContext,
	type IntersectAllValidatorInputs,
	type IntersectAllValidatorOutputs,
	type RequestMiddleware,
	type RequestMiddlewareAfterMiddleware,
	type RequestMiddlewareAfterServer,
	type RequestMiddlewareOptions,
	type RequestMiddlewareServer,
	type RequestMiddlewareServerFnResult,
	type RequestMiddlewareWithTypes,
	type RequestServerFn,
	type RequestServerNextFn,
	type RequestServerNextFnOptions,
	type RequestServerOptions,
	type RequestServerResult,
} from "./createMiddleware";
export type {
	CompiledFetcherFn,
	CompiledFetcherFnOptions,
	Fetcher,
	FetcherBaseOptions,
	Method,
	MiddlewareFn,
	NextFn,
	OptionalFetcher,
	RequiredFetcher,
	RscStream,
	ServerFn,
	ServerFnBaseOptions,
	ServerFnBuilder,
	ServerFnCtx,
	ServerFnMiddlewareOptions,
	ServerFnMiddlewareResult,
} from "./createServerFn";
export {
	applyMiddleware,
	createServerFn,
	executeMiddleware,
	execValidator,
	flattenMiddlewares,
} from "./createServerFn";
export type {
	AnyStartInstance,
	AnyStartInstanceOptions,
	StartInstance,
} from "./createStart";
export { createStart } from "./createStart";
export { createClientOnlyFn, createServerOnlyFn } from "./envOnly";
export { getDefaultSerovalPlugins } from "./getDefaultSerovalPlugins";
export { getGlobalStartContext } from "./getGlobalStartContext";

export { getRouterInstance } from "./getRouterInstance";
export type * from "./serverRoute";
export type * from "./startEntry";
