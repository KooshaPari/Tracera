"use strict";

Object.defineProperty(exports, "__esModule", {
	value: true,
});
exports.default = _createForOfIteratorHelper;
var _unsupportedIterableToArray = require("./unsupportedIterableToArray.js");
function _createForOfIteratorHelper(o, allowArrayLike) {
	var it =
		(typeof Symbol !== "undefined" && o[Symbol.iterator]) || o["@@iterator"];
	if (!it) {
		if (
			Array.isArray(o) ||
			(it = (0, _unsupportedIterableToArray.default)(o)) ||
			(allowArrayLike && o && typeof o.length === "number")
		) {
			if (it) o = it;
			var i = 0;
			var F = () => {};
			return {
				s: F,
				n: () => {
					if (i >= o.length) {
						return {
							done: true,
						};
					}
					return {
						done: false,
						value: o[i++],
					};
				},
				e: (e) => {
					throw e;
				},
				f: F,
			};
		}
		throw new TypeError(
			"Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.",
		);
	}
	var normalCompletion = true,
		didErr = false,
		err;
	return {
		s: () => {
			it = it.call(o);
		},
		n: () => {
			var step = it.next();
			normalCompletion = step.done;
			return step;
		},
		e: (e) => {
			didErr = true;
			err = e;
		},
		f: () => {
			try {
				if (!normalCompletion && it["return"] != null) {
					it["return"]();
				}
			} finally {
				if (didErr) throw err;
			}
		},
	};
}

//# sourceMappingURL=createForOfIteratorHelper.js.map
