"use strict";
var isPrototypeOf = require("../../internals/object-is-prototype-of");
var method = require("../array/virtual/for-each");

var ArrayPrototype = Array.prototype;

module.exports = (it) => {
	var own = it.forEach;
	return it === ArrayPrototype ||
		(isPrototypeOf(ArrayPrototype, it) && own === ArrayPrototype.forEach)
		? method
		: own;
};
