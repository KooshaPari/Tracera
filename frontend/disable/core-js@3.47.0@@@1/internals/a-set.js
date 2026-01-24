"use strict";
var has = require("../internals/set-helpers").has;

// Perform ? RequireInternalSlot(M, [[SetData]])
module.exports = (it) => {
	has(it);
	return it;
};
