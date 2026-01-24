export type { HandlerCallback } from "@tanstack/router-core/ssr/server";
export {
	attachRouterServerSsrUtils,
	createRequestHandler,
	defineHandlerCallback,
	transformPipeableStreamWithRouter,
	transformReadableStreamWithRouter,
} from "@tanstack/router-core/ssr/server";
export { HEADERS } from "./constants";
export type { CustomizeStartHandler } from "./createStartHandler";
export { createStartHandler } from "./createStartHandler";

export * from "./h3";
export { handleServerAction } from "./server-functions-handler";
export type {
	AnyRouteMethodsBuilder,
	AnyServerRoute,
	AnyServerRouteWithTypes,
	AssignAllMethodContext,
	CreateServerFileRoute,
	MergeMethodMiddlewares,
	ResolveAllServerContext,
	ServerFileRoutesByPath,
	ServerRoute,
	ServerRouteAddFileChildrenFn,
	ServerRouteAfterMethods,
	ServerRouteAfterMiddleware,
	ServerRouteManifest,
	ServerRouteMethod,
	ServerRouteMethodBuilder,
	ServerRouteMethodBuilderAfterHandler,
	ServerRouteMethodBuilderAfterMiddleware,
	ServerRouteMethodBuilderHandler,
	ServerRouteMethodBuilderMiddleware,
	ServerRouteMethodBuilderOptions,
	ServerRouteMethodBuilderTypes,
	ServerRouteMethodBuilderWithTypes,
	ServerRouteMethodHandlerCtx,
	ServerRouteMethodHandlerFn,
	ServerRouteMethodRecordValue,
	ServerRouteMethods,
	ServerRouteMethodsOptions,
	ServerRouteMethodsRecord,
	ServerRouteMiddleware,
	ServerRouteOptions,
	ServerRouteTypes,
	ServerRouteVerb,
	ServerRouteWithTypes,
} from "./serverRoute";
export {
	createServerFileRoute,
	createServerRootRoute,
	createServerRoute,
} from "./serverRoute";
export * from "./virtual-modules";
