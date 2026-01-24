Object.defineProperty(exports, "__esModule", {
	value: true,
});

exports.default = (model, calc) => {
	var fn = function fn(buf, previous) {
		return calc(buf, previous) >>> 0;
	};
	fn.signed = calc;
	fn.unsigned = fn;
	fn.model = model;

	return fn;
};
