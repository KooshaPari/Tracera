"use strict";
var uncurryThis = require("../internals/function-uncurry-this");
var iterateSimple = require("../internals/iterate-simple");
var MapHelpers = require("../internals/map-helpers");

var Map = MapHelpers.Map;
var MapPrototype = MapHelpers.proto;
var forEach = uncurryThis(MapPrototype.forEach);
var entries = uncurryThis(MapPrototype.entries);
var next = entries(new Map()).next;

module.exports = (map, fn, interruptible) =>
	interruptible
		? iterateSimple({ iterator: entries(map), next: next }, (entry) =>
				fn(entry[1], entry[0]),
			)
		: forEach(map, fn);
