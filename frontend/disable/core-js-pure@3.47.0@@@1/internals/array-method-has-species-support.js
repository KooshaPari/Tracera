"use strict";
var fails = require("../internals/fails");
var wellKnownSymbol = require("../internals/well-known-symbol");
var V8_VERSION = require("../internals/environment-v8-version");

var SPECIES = wellKnownSymbol("species");

module.exports = (METHOD_NAME) => {
	// We can't use this feature detection in V8 since it causes
	// deoptimization and serious performance degradation
	// https://github.com/zloirock/core-js/issues/677
	return (
		V8_VERSION >= 51 ||
		!fails(() => {
			var array = [];
			var constructor = (array.constructor = {});
			constructor[SPECIES] = () => ({ foo: 1 });
			return array[METHOD_NAME](Boolean).foo !== 1;
		})
	);
};
