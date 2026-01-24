"use strict";
var $RangeError = RangeError;

module.exports = (it) => {
	// eslint-disable-next-line no-self-compare -- NaN check
	if (it === it) return it;
	throw new $RangeError("NaN is not allowed");
};
