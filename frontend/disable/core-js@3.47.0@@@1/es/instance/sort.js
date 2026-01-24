"use strict";
var isPrototypeOf = require("../../internals/object-is-prototype-of");
var method = require("../array/virtual/sort");

var ArrayPrototype = Array.prototype;

module.exports = (it) => {
	var own = it.sort;
	return it === ArrayPrototype ||
		(isPrototypeOf(ArrayPrototype, it) && own === ArrayPrototype.sort)
		? method
		: own;
};
