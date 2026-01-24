var makeDom = require("../utils").makeDom;
var traversal = require("../..");
var assert = require("assert");

describe("traversal", () => {
	describe("hasAttrib", () => {
		var hasAttrib = traversal.hasAttrib;

		it("doesn't throw on text nodes", () => {
			var dom = makeDom("textnode");
			assert.doesNotThrow(() => {
				hasAttrib(dom[0], "some-attrib");
			});
		});
	});
});
