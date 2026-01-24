"use strict";
var SetHelpers = require("../internals/set-helpers");
var iterate = require("../internals/set-iterate");

var Set = SetHelpers.Set;
var add = SetHelpers.add;

module.exports = (set) => {
	var result = new Set();
	iterate(set, (it) => {
		add(result, it);
	});
	return result;
};
