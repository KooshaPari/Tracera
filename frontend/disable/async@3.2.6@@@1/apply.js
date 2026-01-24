Object.defineProperty(exports, "__esModule", {
	value: true,
});

exports.default =
	(fn, ...args) =>
	(...callArgs) =>
		fn(...args, ...callArgs);

module.exports = exports.default;
