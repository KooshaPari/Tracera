var DomUtils = require("../..");
var fixture = require("../fixture");
var assert = require("assert");

// Set up expected structures
var expected = {
	idAsdf: fixture[1],
	tag2: [],
	typeScript: [],
};
for (var idx = 0; idx < 20; ++idx) {
	expected.tag2.push(fixture[idx * 2 + 1].children[5]);
	expected.typeScript.push(fixture[idx * 2 + 1].children[1]);
}

describe("legacy", () => {
	describe("getElements", () => {
		var getElements = DomUtils.getElements;
		it("returns the node with the specified ID", () => {
			assert.deepEqual(getElements({ id: "asdf" }, fixture, true, 1), [
				expected.idAsdf,
			]);
		});
		it("returns empty array for unknown IDs", () => {
			assert.deepEqual(getElements({ id: "asdfs" }, fixture, true), []);
		});
		it("returns the nodes with the specified tag name", () => {
			assert.deepEqual(
				getElements({ tag_name: "tag2" }, fixture, true),
				expected.tag2,
			);
		});
		it("returns empty array for unknown tag names", () => {
			assert.deepEqual(getElements({ tag_name: "asdfs" }, fixture, true), []);
		});
		it("returns the nodes with the specified tag type", () => {
			assert.deepEqual(
				getElements({ tag_type: "script" }, fixture, true),
				expected.typeScript,
			);
		});
		it("returns empty array for unknown tag types", () => {
			assert.deepEqual(getElements({ tag_type: "video" }, fixture, true), []);
		});
	});

	describe("getElementById", () => {
		var getElementById = DomUtils.getElementById;
		it("returns the specified node", () => {
			assert.equal(expected.idAsdf, getElementById("asdf", fixture, true));
		});
		it("returns `null` for unknown IDs", () => {
			assert.equal(null, getElementById("asdfs", fixture, true));
		});
	});

	describe("getElementsByTagName", () => {
		var getElementsByTagName = DomUtils.getElementsByTagName;
		it("returns the specified nodes", () => {
			assert.deepEqual(
				getElementsByTagName("tag2", fixture, true),
				expected.tag2,
			);
		});
		it("returns empty array for unknown tag names", () => {
			assert.deepEqual(getElementsByTagName("tag23", fixture, true), []);
		});
	});

	describe("getElementsByTagType", () => {
		var getElementsByTagType = DomUtils.getElementsByTagType;
		it("returns the specified nodes", () => {
			assert.deepEqual(
				getElementsByTagType("script", fixture, true),
				expected.typeScript,
			);
		});
		it("returns empty array for unknown tag types", () => {
			assert.deepEqual(getElementsByTagType("video", fixture, true), []);
		});
	});

	describe("getOuterHTML", () => {
		var getOuterHTML = DomUtils.getOuterHTML;
		it("Correctly renders the outer HTML", () => {
			assert.equal(
				getOuterHTML(fixture[1]),
				'<tag1 id="asdf"> <script>text</script> <!-- comment --> <tag2> text </tag2></tag1>',
			);
		});
	});

	describe("getInnerHTML", () => {
		var getInnerHTML = DomUtils.getInnerHTML;
		it("Correctly renders the inner HTML", () => {
			assert.equal(
				getInnerHTML(fixture[1]),
				" <script>text</script> <!-- comment --> <tag2> text </tag2>",
			);
		});
	});
});
