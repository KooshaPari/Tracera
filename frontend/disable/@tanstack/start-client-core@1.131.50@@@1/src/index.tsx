export type {
	DehydratedRouter,
	JsonResponse,
} from "@tanstack/router-core/ssr/client";

export { hydrate, json, mergeHeaders } from "@tanstack/router-core/ssr/client";
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
	type AssignAllServerContext,
	createMiddleware,
	type FunctionClientResultWithContext,
	type FunctionMiddleware,
	type FunctionMiddlewareAfterClient,
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
} from "./createMiddleware";
export type {
	CompiledFetcherFn,
	CompiledFetcherFnOptions,
	Fetcher,
	FetcherBaseOptions,
	FetcherData,
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
	ServerFnResponseType,
	ServerFnType,
	StaticCachedResult,
} from "./createServerFn";
export {
	applyMiddleware,
	createServerFn,
	executeMiddleware,
	execValidator,
	extractFormDataContext,
	flattenMiddlewares,
	serverFnBaseToMiddleware,
	serverFnStaticCache,
} from "./createServerFn";
export { clientOnly, serverOnly } from "./envOnly";
export {
	globalMiddleware,
	registerGlobalMiddleware,
} from "./registerGlobalMiddleware";
export type {
	Serializable,
	SerializerExtensions,
	SerializerParse,
	SerializerParseBy,
	SerializerStringify,
	SerializerStringifyBy,
	StartSerializer,
} from "./serializer";
export { startSerializer } from "./serializer";
