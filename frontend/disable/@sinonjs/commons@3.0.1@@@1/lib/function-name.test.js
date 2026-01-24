var jsc = require("jsverify");
var refute = require("@sinonjs/referee-sinon").refute;

var functionName = require("./function-name");

describe("function-name", () => {
	it("should return empty string if func is falsy", () => {
		jsc.assertForall("falsy", (fn) => functionName(fn) === "");
	});

	it("should use displayName by default", () => {
		jsc.assertForall("nestring", (displayName) => {
			var fn = { displayName: displayName };

			return functionName(fn) === fn.displayName;
		});
	});

	it("should use name if displayName is not available", () => {
		jsc.assertForall("nestring", (name) => {
			var fn = { name: name };

			return functionName(fn) === fn.name;
		});
	});

	it("should fallback to string parsing", () => {
		jsc.assertForall("nat", (naturalNumber) => {
			var name = `fn${naturalNumber}`;
			var fn = {
				toString: () => `\nfunction ${name}`,
			};

			return functionName(fn) === name;
		});
	});

	it("should not fail when a name cannot be found", () => {
		refute.exception(() => {
			var fn = {
				toString: () => "\nfunction (",
			};

			functionName(fn);
		});
	});

	it("should not fail when toString is undefined", () => {
		refute.exception(() => {
			functionName(Object.create(null));
		});
	});

	it("should not fail when toString throws", () => {
		refute.exception(() => {
			var fn;
			try {
				// eslint-disable-next-line no-eval
				fn = eval("(function*() {})")().constructor;
			} catch (e) {
				// env doesn't support generators
				return;
			}

			functionName(fn);
		});
	});
});
