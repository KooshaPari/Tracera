"use strict";
var call = require("../internals/function-call");
var hasOwn = require("../internals/has-own-property");
var isPrototypeOf = require("../internals/object-is-prototype-of");
var regExpFlagsDetection = require("../internals/regexp-flags-detection");
var regExpFlagsGetterImplementation = require("../internals/regexp-flags");

var RegExpPrototype = RegExp.prototype;

module.exports = regExpFlagsDetection.correct
	? (it) => it.flags
	: (it) =>
			!regExpFlagsDetection.correct &&
			isPrototypeOf(RegExpPrototype, it) &&
			!hasOwn(it, "flags")
				? call(regExpFlagsGetterImplementation, it)
				: it.flags;
