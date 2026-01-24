"use strict";

Object.defineProperty(exports, "__esModule", {
	value: true,
});
exports.default = _importDeferProxy;
function _importDeferProxy(init) {
	var ns = null;
	var constValue = (v) => () => v;
	var proxy = (run) => (_target, p, receiver) => {
		if (ns === null) ns = init();
		return run(ns, p, receiver);
	};
	return new Proxy(
		{},
		{
			defineProperty: constValue(false),
			deleteProperty: constValue(false),
			get: proxy(Reflect.get),
			getOwnPropertyDescriptor: proxy(Reflect.getOwnPropertyDescriptor),
			getPrototypeOf: constValue(null),
			isExtensible: constValue(false),
			has: proxy(Reflect.has),
			ownKeys: proxy(Reflect.ownKeys),
			preventExtensions: constValue(true),
			set: constValue(false),
			setPrototypeOf: constValue(false),
		},
	);
}

//# sourceMappingURL=importDeferProxy.js.map
