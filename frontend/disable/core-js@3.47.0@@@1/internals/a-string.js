"use strict";
var $TypeError = TypeError;

module.exports = (argument) => {
	if (typeof argument == "string") return argument;
	throw new $TypeError("Argument is not a string");
};
