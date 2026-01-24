"use strict";
var isPrototypeOf = require("../internals/object-is-prototype-of");

var $TypeError = TypeError;

module.exports = (it, Prototype) => {
	if (isPrototypeOf(Prototype, it)) return it;
	throw new $TypeError("Incorrect invocation");
};
