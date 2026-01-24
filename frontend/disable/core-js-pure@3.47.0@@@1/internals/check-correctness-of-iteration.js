"use strict";
var wellKnownSymbol = require("../internals/well-known-symbol");

var ITERATOR = wellKnownSymbol("iterator");
var SAFE_CLOSING = false;

try {
	var called = 0;
	var iteratorWithReturn = {
		next: () => ({ done: !!called++ }),
		return: () => {
			SAFE_CLOSING = true;
		},
	};
	// eslint-disable-next-line unicorn/no-immediate-mutation -- ES3 syntax limitation
	iteratorWithReturn[ITERATOR] = function () {
		return this;
	};
	// eslint-disable-next-line es/no-array-from, no-throw-literal -- required for testing
	Array.from(iteratorWithReturn, () => {
		throw 2;
	});
} catch (error) {
	/* empty */
}

module.exports = (exec, SKIP_CLOSING) => {
	try {
		if (!SKIP_CLOSING && !SAFE_CLOSING) return false;
	} catch (error) {
		return false;
	} // workaround of old WebKit + `eval` bug
	var ITERATION_SUPPORT = false;
	try {
		var object = {};
		// eslint-disable-next-line unicorn/no-immediate-mutation -- ES3 syntax limitation
		object[ITERATOR] = () => ({
			next: () => ({ done: (ITERATION_SUPPORT = true) }),
		});
		exec(object);
	} catch (error) {
		/* empty */
	}
	return ITERATION_SUPPORT;
};
