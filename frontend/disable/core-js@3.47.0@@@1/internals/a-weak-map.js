"use strict";
var has = require("../internals/weak-map-helpers").has;

// Perform ? RequireInternalSlot(M, [[WeakMapData]])
module.exports = (it) => {
	has(it);
	return it;
};
