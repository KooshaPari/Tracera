import { decodeBuffer, encodeBuffer } from "./chunk-6HYIRFX2.mjs";
import { IS_PATCHED_MODULE } from "./chunk-6YM4PLBI.mjs";
import {
	createRequestId,
	deleteGlobalSymbol,
	FetchResponse,
	getGlobalSymbol,
	INTERNAL_REQUEST_ID_HEADER_NAME,
	Interceptor,
	InterceptorReadyState,
	RequestController,
} from "./chunk-JXGB54LE.mjs";
import { BatchInterceptor } from "./chunk-SQ6RHTJR.mjs";
import { getRawRequest } from "./chunk-YWNGXXUQ.mjs";

// src/utils/getCleanUrl.ts
function getCleanUrl(url, isAbsolute = true) {
	return [isAbsolute && url.origin, url.pathname].filter(Boolean).join("");
}
export {
	BatchInterceptor,
	FetchResponse,
	INTERNAL_REQUEST_ID_HEADER_NAME,
	IS_PATCHED_MODULE,
	Interceptor,
	InterceptorReadyState,
	RequestController,
	createRequestId,
	decodeBuffer,
	deleteGlobalSymbol,
	encodeBuffer,
	getCleanUrl,
	getGlobalSymbol,
	getRawRequest,
};
//# sourceMappingURL=index.mjs.map
