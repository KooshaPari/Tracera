"use strict";
var $TypeError = TypeError;

module.exports = (passed, required) => {
	if (passed < required) throw new $TypeError("Not enough arguments");
	return passed;
};
