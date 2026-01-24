"use strict";
/* eslint-disable no-unused-vars -- required for functions `.length` */
var $ = require("../internals/export");
var globalThis = require("../internals/global-this");
var apply = require("../internals/function-apply");
var wrapErrorConstructorWithCause = require("../internals/wrap-error-constructor-with-cause");

var WEB_ASSEMBLY = "WebAssembly";
var WebAssembly = globalThis[WEB_ASSEMBLY];

// eslint-disable-next-line es/no-error-cause -- feature detection
var FORCED = new Error("e", { cause: 7 }).cause !== 7;

var exportGlobalErrorCauseWrapper = (ERROR_NAME, wrapper) => {
	var O = {};
	// eslint-disable-next-line unicorn/no-immediate-mutation -- ES3 syntax limitation
	O[ERROR_NAME] = wrapErrorConstructorWithCause(ERROR_NAME, wrapper, FORCED);
	$({ global: true, constructor: true, arity: 1, forced: FORCED }, O);
};

var exportWebAssemblyErrorCauseWrapper = (ERROR_NAME, wrapper) => {
	if (WebAssembly && WebAssembly[ERROR_NAME]) {
		var O = {};
		// eslint-disable-next-line unicorn/no-immediate-mutation -- ES3 syntax limitation
		O[ERROR_NAME] = wrapErrorConstructorWithCause(
			WEB_ASSEMBLY + "." + ERROR_NAME,
			wrapper,
			FORCED,
		);
		$(
			{
				target: WEB_ASSEMBLY,
				stat: true,
				constructor: true,
				arity: 1,
				forced: FORCED,
			},
			O,
		);
	}
};

// https://tc39.es/ecma262/#sec-nativeerror
exportGlobalErrorCauseWrapper(
	"Error",
	(init) =>
		function Error(message) {
			return apply(init, this, arguments);
		},
);
exportGlobalErrorCauseWrapper(
	"EvalError",
	(init) =>
		function EvalError(message) {
			return apply(init, this, arguments);
		},
);
exportGlobalErrorCauseWrapper(
	"RangeError",
	(init) =>
		function RangeError(message) {
			return apply(init, this, arguments);
		},
);
exportGlobalErrorCauseWrapper(
	"ReferenceError",
	(init) =>
		function ReferenceError(message) {
			return apply(init, this, arguments);
		},
);
exportGlobalErrorCauseWrapper(
	"SyntaxError",
	(init) =>
		function SyntaxError(message) {
			return apply(init, this, arguments);
		},
);
exportGlobalErrorCauseWrapper(
	"TypeError",
	(init) =>
		function TypeError(message) {
			return apply(init, this, arguments);
		},
);
exportGlobalErrorCauseWrapper(
	"URIError",
	(init) =>
		function URIError(message) {
			return apply(init, this, arguments);
		},
);
exportWebAssemblyErrorCauseWrapper(
	"CompileError",
	(init) =>
		function CompileError(message) {
			return apply(init, this, arguments);
		},
);
exportWebAssemblyErrorCauseWrapper(
	"LinkError",
	(init) =>
		function LinkError(message) {
			return apply(init, this, arguments);
		},
);
exportWebAssemblyErrorCauseWrapper(
	"RuntimeError",
	(init) =>
		function RuntimeError(message) {
			return apply(init, this, arguments);
		},
);
