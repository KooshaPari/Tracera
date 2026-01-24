var refute = require("@sinonjs/referee-sinon").refute;
var copyPrototypeMethods = require("./copy-prototype-methods");

describe("copyPrototypeMethods", () => {
	it("does not throw for Map", () => {
		refute.exception(() => {
			copyPrototypeMethods(Map.prototype);
		});
	});
});
