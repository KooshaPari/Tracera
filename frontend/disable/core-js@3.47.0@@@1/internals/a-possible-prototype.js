"use strict";
var isPossiblePrototype = require("../internals/is-possible-prototype");

var $String = String;
var $TypeError = TypeError;

module.exports = (argument) => {
	if (isPossiblePrototype(argument)) return argument;
	throw new $TypeError("Can't set " + $String(argument) + " as a prototype");
};
