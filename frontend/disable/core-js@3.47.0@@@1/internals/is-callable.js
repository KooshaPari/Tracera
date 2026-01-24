"use strict";
// https://tc39.es/ecma262/#sec-IsHTMLDDA-internal-slot
var documentAll = typeof document == "object" && document.all;

// `IsCallable` abstract operation
// https://tc39.es/ecma262/#sec-iscallable
// eslint-disable-next-line unicorn/no-typeof-undefined -- required for testing
module.exports =
	typeof documentAll == "undefined" && documentAll !== undefined
		? (argument) => typeof argument == "function" || argument === documentAll
		: (argument) => typeof argument == "function";
