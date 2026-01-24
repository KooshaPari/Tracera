"use strict";
module.exports = (bitmap, value) => ({
	enumerable: !(bitmap & 1),
	configurable: !(bitmap & 2),
	writable: !(bitmap & 4),
	value: value,
});
