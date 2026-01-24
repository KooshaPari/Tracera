Object.defineProperty(exports, "__esModule", { value: true });
var EmptySet = /** @class */ (() => {
	function EmptySet() {}
	Object.defineProperty(EmptySet.prototype, "size", {
		get: () => 0,
		enumerable: true,
		configurable: true,
	});
	EmptySet.prototype.add = (value) => {
		throw new Error("Cannot add to an empty set.");
	};
	EmptySet.prototype.clear = () => {
		// no-op
	};
	EmptySet.prototype.delete = (value) => false;
	EmptySet.prototype.forEach = (callbackfn, thisArg) => {
		// no-op
	};
	EmptySet.prototype.has = (value) => false;
	EmptySet.prototype[Symbol.iterator] = () => new EmptySetIterator();
	EmptySet.prototype.entries = () => new EmptySetIterator();
	EmptySet.prototype.keys = () => new EmptySetIterator();
	EmptySet.prototype.values = () => new EmptySetIterator();
	Object.defineProperty(EmptySet.prototype, Symbol.toStringTag, {
		get: () => "EmptySet",
		enumerable: true,
		configurable: true,
	});
	return EmptySet;
})();
exports.EmptySet = EmptySet;
var EmptySetIterator = /** @class */ (() => {
	function EmptySetIterator() {}
	EmptySetIterator.prototype[Symbol.iterator] = function () {
		return this;
	};
	EmptySetIterator.prototype.next = () => ({ done: true, value: null });
	return EmptySetIterator;
})();
//# sourceMappingURL=EmptySet.js.map
