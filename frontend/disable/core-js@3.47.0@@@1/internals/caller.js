"use strict";
module.exports = (methodName, numArgs) =>
	numArgs === 1
		? (object, arg) => object[methodName](arg)
		: (object, arg1, arg2) => object[methodName](arg1, arg2);
