"use strict";
var $ = require("../internals/export");
var difference = require("../internals/set-difference");
var fails = require("../internals/fails");
var setMethodAcceptSetLike = require("../internals/set-method-accept-set-like");

var SET_LIKE_INCORRECT_BEHAVIOR = !setMethodAcceptSetLike(
	"difference",
	(result) => result.size === 0,
);

var FORCED =
	SET_LIKE_INCORRECT_BEHAVIOR ||
	fails(() => {
		// https://bugs.webkit.org/show_bug.cgi?id=288595
		var setLike = {
			size: 1,
			has: () => true,
			keys: () => {
				var index = 0;
				return {
					next: () => {
						var done = index++ > 1;
						if (baseSet.has(1)) baseSet.clear();
						return { done: done, value: 2 };
					},
				};
			},
		};
		// eslint-disable-next-line es/no-set -- testing
		var baseSet = new Set([1, 2, 3, 4]);
		// eslint-disable-next-line es/no-set-prototype-difference -- testing
		return baseSet.difference(setLike).size !== 3;
	});

// `Set.prototype.difference` method
// https://tc39.es/ecma262/#sec-set.prototype.difference
$(
	{ target: "Set", proto: true, real: true, forced: FORCED },
	{
		difference: difference,
	},
);
