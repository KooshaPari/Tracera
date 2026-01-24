"use strict";
var iterateSimple = require("../internals/iterate-simple");

module.exports = (map, fn, interruptible) =>
	interruptible
		? iterateSimple(map.entries(), (entry) => fn(entry[1], entry[0]), true)
		: map.forEach(fn);
