Object.defineProperty(exports, "__esModule", {
	value: true,
});

exports.default =
	(...args) =>
	(...ignoredArgs /*, callback*/) => {
		var callback = ignoredArgs.pop();
		return callback(null, ...args);
	};

module.exports = exports.default;
