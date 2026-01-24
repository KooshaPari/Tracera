"use strict";
var has = require("../internals/map-helpers").has;

// Perform ? RequireInternalSlot(M, [[MapData]])
module.exports = (it) => {
	has(it);
	return it;
};
