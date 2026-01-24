"use strict";
var iterateSimple = require("../internals/iterate-simple");

module.exports = (set, fn, interruptible) =>
	interruptible ? iterateSimple(set.keys(), fn, true) : set.forEach(fn);
