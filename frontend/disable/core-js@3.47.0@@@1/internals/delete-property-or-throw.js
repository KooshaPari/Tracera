"use strict";
var tryToString = require("../internals/try-to-string");

var $TypeError = TypeError;

module.exports = (O, P) => {
	if (!delete O[P])
		throw new $TypeError(
			"Cannot delete property " + tryToString(P) + " of " + tryToString(O),
		);
};
