// src/utils/node/index.ts
import { ClientRequest } from "http";
import { invariant } from "outvariant";
import { Readable } from "stream";
import { getRawRequest } from "./chunk-YWNGXXUQ.mjs";

var kRawRequestBodyStream = Symbol("kRawRequestBodyStream");
function getClientRequestBodyStream(request) {
	const rawRequest = getRawRequest(request);
	invariant(
		rawRequest instanceof ClientRequest,
		`Failed to retrieve raw request body stream: request is not an instance of "http.ClientRequest". Note that you can only use the "getClientRequestBodyStream" function with the requests issued by "http.clientRequest".`,
	);
	const requestBodyStream = Reflect.get(request, kRawRequestBodyStream);
	invariant(
		requestBodyStream instanceof Readable,
		"Failed to retrieve raw request body stream: corrupted stream (%s)",
		typeof requestBodyStream,
	);
	return requestBodyStream;
}
function setRawRequestBodyStream(request, stream) {
	Reflect.set(request, kRawRequestBodyStream, stream);
}

export { getClientRequestBodyStream, setRawRequestBodyStream };
//# sourceMappingURL=chunk-GKN5RBVR.mjs.map
