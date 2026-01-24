var assert = require("@sinonjs/referee-sinon").assert;
var sinon = require("@sinonjs/referee-sinon").sinon;
var every = require("./every");

describe("util/core/every", () => {
	it("returns true when the callback function returns true for every element in an iterable", () => {
		var obj = [true, true, true, true];
		var allTrue = every(obj, (val) => val);

		assert(allTrue);
	});

	it("returns false when the callback function returns false for any element in an iterable", () => {
		var obj = [true, true, true, false];
		var result = every(obj, (val) => val);

		assert.isFalse(result);
	});

	it("calls the given callback once for each item in an iterable until it returns false", () => {
		var iterableOne = [true, true, true, true];
		var iterableTwo = [true, true, false, true];
		var callback = sinon.spy((val) => val);

		every(iterableOne, callback);
		assert.equals(callback.callCount, 4);

		callback.resetHistory();

		every(iterableTwo, callback);
		assert.equals(callback.callCount, 3);
	});
});
