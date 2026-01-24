"use strict";
var getBuiltIn = require("../internals/get-built-in");

var createSetLike = (size) => ({
	size: size,
	has: () => false,
	keys: () => ({
		next: () => ({ done: true }),
	}),
});

var createSetLikeWithInfinitySize = (size) => ({
	size: size,
	has: () => true,
	keys: () => {
		throw new Error("e");
	},
});

module.exports = (name, callback) => {
	var Set = getBuiltIn("Set");
	try {
		new Set()[name](createSetLike(0));
		try {
			// late spec change, early WebKit ~ Safari 17 implementation does not pass it
			// https://github.com/tc39/proposal-set-methods/pull/88
			// also covered engines with
			// https://bugs.webkit.org/show_bug.cgi?id=272679
			new Set()[name](createSetLike(-1));
			return false;
		} catch (error2) {
			if (!callback) return true;
			// early V8 implementation bug
			// https://issues.chromium.org/issues/351332634
			try {
				new Set()[name](createSetLikeWithInfinitySize(-Infinity));
				return false;
			} catch (error) {
				var set = new Set([1, 2]);
				return callback(set[name](createSetLikeWithInfinitySize(Infinity)));
			}
		}
	} catch (error) {
		return false;
	}
};
