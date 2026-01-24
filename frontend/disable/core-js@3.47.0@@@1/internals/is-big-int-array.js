"use strict";
var classof = require("../internals/classof");

module.exports = (it) => {
	var klass = classof(it);
	return klass === "BigInt64Array" || klass === "BigUint64Array";
};
