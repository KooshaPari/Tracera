"use strict";
var $TypeError = TypeError;

module.exports = (argument) => {
	if (typeof argument == "number") return argument;
	throw new $TypeError("Argument is not a number");
};
