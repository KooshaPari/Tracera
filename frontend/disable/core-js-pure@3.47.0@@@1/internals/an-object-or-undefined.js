"use strict";
var isObject = require("../internals/is-object");

var $String = String;
var $TypeError = TypeError;

module.exports = (argument) => {
	if (argument === undefined || isObject(argument)) return argument;
	throw new $TypeError($String(argument) + " is not an object or undefined");
};
