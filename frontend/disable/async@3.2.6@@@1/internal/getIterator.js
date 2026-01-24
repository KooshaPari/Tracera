Object.defineProperty(exports, "__esModule", {
	value: true,
});

exports.default = (coll) => coll[Symbol.iterator] && coll[Symbol.iterator]();

module.exports = exports.default;
