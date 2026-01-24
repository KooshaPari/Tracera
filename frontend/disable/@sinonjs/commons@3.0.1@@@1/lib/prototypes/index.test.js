var assert = require("@sinonjs/referee-sinon").assert;

var arrayProto = require("./index").array;
var functionProto = require("./index").function;
var mapProto = require("./index").map;
var objectProto = require("./index").object;
var setProto = require("./index").set;
var stringProto = require("./index").string;
var throwsOnProto = require("./throws-on-proto");

describe("prototypes", () => {
	describe(".array", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		verifyProperties(arrayProto, Array);
	});
	describe(".function", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		verifyProperties(functionProto, Function);
	});
	describe(".map", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		verifyProperties(mapProto, Map);
	});
	describe(".object", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		verifyProperties(objectProto, Object);
	});
	describe(".set", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		verifyProperties(setProto, Set);
	});
	describe(".string", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		verifyProperties(stringProto, String);
	});
});

function verifyProperties(p, origin) {
	var disallowedProperties = ["size", "caller", "callee", "arguments"];
	if (throwsOnProto) {
		disallowedProperties.push("__proto__");
	}

	it("should have all the methods of the origin prototype", () => {
		var methodNames = Object.getOwnPropertyNames(origin.prototype).filter(
			(name) => {
				if (disallowedProperties.includes(name)) {
					return false;
				}

				return typeof origin.prototype[name] === "function";
			},
		);

		methodNames.forEach((name) => {
			assert.isTrue(Object.hasOwn(p, name), name);
		});
	});
}
