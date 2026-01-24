"use strict";
var call = require("../internals/function-call");
var map = require("../internals/async-iterator-map");

var callback = (value, counter) => [counter, value];

// `AsyncIterator.prototype.indexed` method
// https://github.com/tc39/proposal-iterator-helpers
module.exports = function indexed() {
	return call(map, this, callback);
};
