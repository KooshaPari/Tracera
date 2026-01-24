"use strict";

Object.defineProperty(exports, "__esModule", {
	value: true,
});
exports.default = _regeneratorAsync;
var _regeneratorAsyncGen = require("./regeneratorAsyncGen.js");
function _regeneratorAsync(innerFn, outerFn, self, tryLocsList, PromiseImpl) {
	var iter = (0, _regeneratorAsyncGen.default)(
		innerFn,
		outerFn,
		self,
		tryLocsList,
		PromiseImpl,
	);
	return iter
		.next()
		.then((result) => (result.done ? result.value : iter.next()));
}

//# sourceMappingURL=regeneratorAsync.js.map
