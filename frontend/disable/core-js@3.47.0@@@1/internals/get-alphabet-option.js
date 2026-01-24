"use strict";
var $TypeError = TypeError;

module.exports = (options) => {
	var alphabet = options && options.alphabet;
	if (
		alphabet === undefined ||
		alphabet === "base64" ||
		alphabet === "base64url"
	)
		return alphabet || "base64";
	throw new $TypeError("Incorrect `alphabet` option");
};
