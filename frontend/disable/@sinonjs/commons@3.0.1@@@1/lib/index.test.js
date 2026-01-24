var assert = require("@sinonjs/referee-sinon").assert;
var index = require("./index");

var expectedMethods = [
	"calledInOrder",
	"className",
	"every",
	"functionName",
	"orderByFirstCall",
	"typeOf",
	"valueToString",
];
var expectedObjectProperties = ["deprecated", "prototypes"];

describe("package", () => {
	// eslint-disable-next-line mocha/no-setup-in-describe
	expectedMethods.forEach((name) => {
		it(`should export a method named ${name}`, () => {
			assert.isFunction(index[name]);
		});
	});

	// eslint-disable-next-line mocha/no-setup-in-describe
	expectedObjectProperties.forEach((name) => {
		it(`should export an object property named ${name}`, () => {
			assert.isObject(index[name]);
		});
	});
});
