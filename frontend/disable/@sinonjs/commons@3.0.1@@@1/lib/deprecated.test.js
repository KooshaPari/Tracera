/* eslint-disable no-console */

var assert = require("@sinonjs/referee-sinon").assert;
var sinon = require("@sinonjs/referee-sinon").sinon;

var deprecated = require("./deprecated");

var msg = "test";

describe("deprecated", () => {
	describe("defaultMsg", () => {
		it("should return a string", () => {
			assert.equals(
				deprecated.defaultMsg("sinon", "someFunc"),
				"sinon.someFunc is deprecated and will be removed from the public API in a future version of sinon.",
			);
		});
	});

	describe("printWarning", () => {
		beforeEach(() => {
			sinon.replace(process, "emitWarning", sinon.fake());
		});

		afterEach(sinon.restore);

		describe("when `process.emitWarning` is defined", () => {
			it("should call process.emitWarning with a msg", () => {
				deprecated.printWarning(msg);
				assert.calledOnceWith(process.emitWarning, msg);
			});
		});

		describe("when `process.emitWarning` is undefined", () => {
			beforeEach(() => {
				sinon.replace(console, "info", sinon.fake());
				sinon.replace(console, "log", sinon.fake());
				process.emitWarning = undefined;
			});

			afterEach(sinon.restore);

			describe("when `console.info` is defined", () => {
				it("should call `console.info` with a message", () => {
					deprecated.printWarning(msg);
					assert.calledOnceWith(console.info, msg);
				});
			});

			describe("when `console.info` is undefined", () => {
				it("should call `console.log` with a message", () => {
					console.info = undefined;
					deprecated.printWarning(msg);
					assert.calledOnceWith(console.log, msg);
				});
			});
		});
	});

	describe("wrap", () => {
		// eslint-disable-next-line mocha/no-setup-in-describe
		var method = sinon.fake();
		var wrapped;

		beforeEach(() => {
			wrapped = deprecated.wrap(method, msg);
		});

		it("should return a wrapper function", () => {
			assert.match(wrapped, sinon.match.func);
		});

		it("should assign the prototype of the passed method", () => {
			assert.equals(method.prototype, wrapped.prototype);
		});

		context("when the passed method has falsy prototype", () => {
			it("should not be assigned to the wrapped method", () => {
				method.prototype = null;
				wrapped = deprecated.wrap(method, msg);
				assert.match(wrapped.prototype, sinon.match.object);
			});
		});

		context("when invoking the wrapped function", () => {
			before(() => {
				sinon.replace(deprecated, "printWarning", sinon.fake());
				wrapped({});
			});

			it("should call `printWarning` before invoking", () => {
				assert.calledOnceWith(deprecated.printWarning, msg);
			});

			it("should invoke the passed method with the given arguments", () => {
				assert.calledOnceWith(method, {});
			});
		});
	});
});
