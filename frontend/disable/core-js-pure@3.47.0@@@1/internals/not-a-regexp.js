"use strict";
var isRegExp = require("../internals/is-regexp");

var $TypeError = TypeError;

module.exports = (it) => {
	if (isRegExp(it)) {
		throw new $TypeError("The method doesn't accept regular expressions");
	}
	return it;
};
