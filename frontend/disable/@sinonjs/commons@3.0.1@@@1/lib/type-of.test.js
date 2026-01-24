var assert = require("@sinonjs/referee-sinon").assert;
var typeOf = require("./type-of");

describe("typeOf", () => {
	it("returns boolean", () => {
		assert.equals(typeOf(false), "boolean");
	});

	it("returns string", () => {
		assert.equals(typeOf("Sinon.JS"), "string");
	});

	it("returns number", () => {
		assert.equals(typeOf(123), "number");
	});

	it("returns object", () => {
		assert.equals(typeOf({}), "object");
	});

	it("returns function", () => {
		assert.equals(
			typeOf(() => undefined),
			"function",
		);
	});

	it("returns undefined", () => {
		assert.equals(typeOf(undefined), "undefined");
	});

	it("returns null", () => {
		assert.equals(typeOf(null), "null");
	});

	it("returns array", () => {
		assert.equals(typeOf([]), "array");
	});

	it("returns regexp", () => {
		assert.equals(typeOf(/.*/), "regexp");
	});

	it("returns date", () => {
		assert.equals(typeOf(new Date()), "date");
	});
});
