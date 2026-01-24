"use strict";
var fails = require("../internals/fails");

module.exports = !fails(() => {
	// eslint-disable-next-line es/no-function-prototype-bind -- safe
	var test = (() => {
		/* empty */
	}).bind();
	// eslint-disable-next-line no-prototype-builtins -- safe
	return typeof test != "function" || Object.hasOwn(test, "prototype");
});
