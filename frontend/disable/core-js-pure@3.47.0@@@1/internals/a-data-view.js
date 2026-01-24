"use strict";
var classof = require("../internals/classof");

var $TypeError = TypeError;

module.exports = (argument) => {
	if (classof(argument) === "DataView") return argument;
	throw new $TypeError("Argument is not a DataView");
};
