"use strict";

Object.defineProperty(exports, "__esModule", {
	value: true,
});
exports.default = _asyncToGenerator;
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) {
	try {
		var info = gen[key](arg);
		var value = info.value;
	} catch (error) {
		reject(error);
		return;
	}
	if (info.done) {
		resolve(value);
	} else {
		Promise.resolve(value).then(_next, _throw);
	}
}
function _asyncToGenerator(fn) {
	return function () {
		var args = arguments;
		return new Promise((resolve, reject) => {
			var gen = fn.apply(this, args);
			function _next(value) {
				asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value);
			}
			function _throw(err) {
				asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err);
			}
			_next(undefined);
		});
	};
}

//# sourceMappingURL=asyncToGenerator.js.map
