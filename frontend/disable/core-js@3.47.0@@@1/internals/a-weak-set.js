"use strict";
var has = require("../internals/weak-set-helpers").has;

// Perform ? RequireInternalSlot(M, [[WeakSetData]])
module.exports = (it) => {
	has(it);
	return it;
};
