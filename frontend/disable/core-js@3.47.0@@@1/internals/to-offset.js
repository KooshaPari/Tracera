"use strict";
var toPositiveInteger = require("../internals/to-positive-integer");

var $RangeError = RangeError;

module.exports = (it, BYTES) => {
	var offset = toPositiveInteger(it);
	if (offset % BYTES) throw new $RangeError("Wrong offset");
	return offset;
};
