import { tail } from "ramda";
import { isFunction, isString } from "ramda-adjunct";
// @ts-expect-error
import treeSitterWasm from "web-tree-sitter/tree-sitter.wasm";

// patch fetch() to let emscripten load the WASM file
const realFetch = globalThis.fetch;
if (isFunction(realFetch)) {
	globalThis.fetch = (...args) => {
		// @ts-expect-error
		if (isString(args[0]) && args[0].endsWith("tree-sitter.wasm")) {
			// @ts-expect-error
			return realFetch.apply(globalThis, [treeSitterWasm, tail(args)]);
		}
		return realFetch.apply(globalThis, args);
	};
}
