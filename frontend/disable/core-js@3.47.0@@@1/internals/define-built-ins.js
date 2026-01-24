"use strict";
var defineBuiltIn = require("../internals/define-built-in");

module.exports = (target, src, options) => {
	for (var key in src) defineBuiltIn(target, key, src[key], options);
	return target;
};
