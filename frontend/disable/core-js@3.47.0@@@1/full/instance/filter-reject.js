"use strict";
var isPrototypeOf = require("../../internals/object-is-prototype-of");
var method = require("../array/virtual/filter-reject");

var ArrayPrototype = Array.prototype;

module.exports = (it) => {
	var own = it.filterReject;
	return it === ArrayPrototype ||
		(isPrototypeOf(ArrayPrototype, it) && own === ArrayPrototype.filterReject)
		? method
		: own;
};
