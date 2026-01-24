"use strict";
var createNonEnumerableProperty = require("../internals/create-non-enumerable-property");

module.exports = (target, key, value, options) => {
	if (options && options.enumerable) target[key] = value;
	else createNonEnumerableProperty(target, key, value);
	return target;
};
