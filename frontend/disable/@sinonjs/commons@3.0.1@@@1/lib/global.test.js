var assert = require("@sinonjs/referee-sinon").assert;
var globalObject = require("./global");

describe("global", () => {
	before(function () {
		if (typeof global === "undefined") {
			this.skip();
		}
	});

	it("is same as global", () => {
		assert.same(globalObject, global);
	});
});
