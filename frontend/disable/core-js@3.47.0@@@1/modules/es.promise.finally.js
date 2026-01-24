"use strict";
var $ = require("../internals/export");
var IS_PURE = require("../internals/is-pure");
var NativePromiseConstructor = require("../internals/promise-native-constructor");
var fails = require("../internals/fails");
var getBuiltIn = require("../internals/get-built-in");
var isCallable = require("../internals/is-callable");
var speciesConstructor = require("../internals/species-constructor");
var promiseResolve = require("../internals/promise-resolve");
var defineBuiltIn = require("../internals/define-built-in");

var NativePromisePrototype =
	NativePromiseConstructor && NativePromiseConstructor.prototype;

// Safari bug https://bugs.webkit.org/show_bug.cgi?id=200829
var NON_GENERIC =
	!!NativePromiseConstructor &&
	fails(() => {
		// eslint-disable-next-line unicorn/no-thenable -- required for testing
		NativePromisePrototype["finally"].call(
			{
				then: () => {
					/* empty */
				},
			},
			() => {
				/* empty */
			},
		);
	});

// `Promise.prototype.finally` method
// https://tc39.es/ecma262/#sec-promise.prototype.finally
$(
	{ target: "Promise", proto: true, real: true, forced: NON_GENERIC },
	{
		finally: function (onFinally) {
			var C = speciesConstructor(this, getBuiltIn("Promise"));
			var isFunction = isCallable(onFinally);
			return this.then(
				isFunction
					? (x) => promiseResolve(C, onFinally()).then(() => x)
					: onFinally,
				isFunction
					? (e) =>
							promiseResolve(C, onFinally()).then(() => {
								throw e;
							})
					: onFinally,
			);
		},
	},
);

// makes sure that native promise-based APIs `Promise#finally` properly works with patched `Promise#then`
if (!IS_PURE && isCallable(NativePromiseConstructor)) {
	var method = getBuiltIn("Promise").prototype["finally"];
	if (NativePromisePrototype["finally"] !== method) {
		defineBuiltIn(NativePromisePrototype, "finally", method, { unsafe: true });
	}
}
