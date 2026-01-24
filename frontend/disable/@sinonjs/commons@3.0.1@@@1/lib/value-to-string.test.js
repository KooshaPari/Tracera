var assert = require("@sinonjs/referee-sinon").assert;
var valueToString = require("./value-to-string");

describe("util/core/valueToString", () => {
	it("returns string representation of an object", () => {
		var obj = {};

		assert.equals(valueToString(obj), obj.toString());
	});

	it("returns 'null' for literal null'", () => {
		assert.equals(valueToString(null), "null");
	});

	it("returns 'undefined' for literal undefined", () => {
		assert.equals(valueToString(undefined), "undefined");
	});
});
