"use strict";
var wellKnownSymbol = require("../internals/well-known-symbol");
var Iterators = require("../internals/iterators");

var ITERATOR = wellKnownSymbol("iterator");
var ArrayPrototype = Array.prototype;

// check on default Array iterator
module.exports = (it) =>
	it !== undefined &&
	(Iterators.Array === it || ArrayPrototype[ITERATOR] === it);
