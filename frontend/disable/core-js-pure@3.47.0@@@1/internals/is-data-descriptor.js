"use strict";
var hasOwn = require("../internals/has-own-property");

module.exports = (descriptor) =>
	descriptor !== undefined &&
	(hasOwn(descriptor, "value") || hasOwn(descriptor, "writable"));
