import type { CreateRpcFn } from "@tanstack/server-functions-plugin";
import { serverFnFetcher } from "@tanstack/start-server-functions-fetcher";

function sanitizeBase(base: string) {
	return base.replace(/^\/|\/$/g, "");
}

export const createClientRpc: CreateRpcFn = (functionId, serverBase) => {
	const sanitizedAppBase = sanitizeBase(process.env.TSS_APP_BASE || "/");
	const sanitizedServerBase = sanitizeBase(serverBase);

	const url = `${sanitizedAppBase ? `/${sanitizedAppBase}` : ``}/${sanitizedServerBase}/${functionId}`;

	const clientFn = (...args: Array<any>) => {
		return serverFnFetcher(url, args, fetch);
	};

	return Object.assign(clientFn, {
		url,
		functionId,
	});
};
