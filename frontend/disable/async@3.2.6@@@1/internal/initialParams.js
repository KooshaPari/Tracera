Object.defineProperty(exports, "__esModule", {
	value: true,
});

exports.default = (fn) =>
	function (...args /*, callback*/) {
		var callback = args.pop();
		return fn.call(this, args, callback);
	};

module.exports = exports.default;
