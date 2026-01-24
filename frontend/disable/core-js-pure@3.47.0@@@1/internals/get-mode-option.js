"use strict";
var $TypeError = TypeError;

module.exports = (options) => {
	var mode = options && options.mode;
	if (
		mode === undefined ||
		mode === "shortest" ||
		mode === "longest" ||
		mode === "strict"
	)
		return mode || "shortest";
	throw new $TypeError("Incorrect `mode` option");
};
