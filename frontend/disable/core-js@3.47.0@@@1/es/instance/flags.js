"use strict";
var isPrototypeOf = require("../../internals/object-is-prototype-of");
var flags = require("../regexp/flags");

var RegExpPrototype = RegExp.prototype;

module.exports = (it) =>
	it === RegExpPrototype || isPrototypeOf(RegExpPrototype, it)
		? flags(it)
		: it.flags;
