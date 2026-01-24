"use strict";
require("../modules/es.iterator.map");
var call = require("../internals/function-call");
var map = require("../internals/iterators-core").IteratorPrototype.map;

var callback = (value, counter) => [counter, value];

// `Iterator.prototype.indexed` method
// https://github.com/tc39/proposal-iterator-helpers
module.exports = function indexed() {
	return call(map, this, callback);
};
