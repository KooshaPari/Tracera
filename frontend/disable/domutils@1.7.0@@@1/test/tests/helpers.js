var makeDom = require("../utils").makeDom;
var helpers = require("../..");
var assert = require("assert");

describe("helpers", () => {
	describe("removeSubsets", () => {
		var removeSubsets = helpers.removeSubsets;
		var dom = makeDom("<div><p><span></span></p><p></p></div>")[0];

		it("removes identical trees", () => {
			var matches = removeSubsets([dom, dom]);
			assert.equal(matches.length, 1);
		});

		it("Removes subsets found first", () => {
			var matches = removeSubsets([dom, dom.children[0].children[0]]);
			assert.equal(matches.length, 1);
		});

		it("Removes subsets found last", () => {
			var matches = removeSubsets([dom.children[0], dom]);
			assert.equal(matches.length, 1);
		});

		it("Does not remove unique trees", () => {
			var matches = removeSubsets([dom.children[0], dom.children[1]]);
			assert.equal(matches.length, 2);
		});
	});

	describe("compareDocumentPosition", () => {
		var compareDocumentPosition = helpers.compareDocumentPosition;
		var markup = "<div><p><span></span></p><a></a></div>";
		var dom = makeDom(markup)[0];
		var p = dom.children[0];
		var span = p.children[0];
		var a = dom.children[1];

		it("reports when the first node occurs before the second indirectly", () => {
			assert.equal(compareDocumentPosition(span, a), 2);
		});

		it("reports when the first node contains the second", () => {
			assert.equal(compareDocumentPosition(p, span), 10);
		});

		it("reports when the first node occurs after the second indirectly", () => {
			assert.equal(compareDocumentPosition(a, span), 4);
		});

		it("reports when the first node is contained by the second", () => {
			assert.equal(compareDocumentPosition(span, p), 20);
		});

		it("reports when the nodes belong to separate documents", () => {
			var other = makeDom(markup)[0].children[0].children[0];

			assert.equal(compareDocumentPosition(span, other), 1);
		});

		it("reports when the nodes are identical", () => {
			assert.equal(compareDocumentPosition(span, span), 0);
		});
	});

	describe("uniqueSort", () => {
		var uniqueSort = helpers.uniqueSort;
		var dom, p, span, a;

		beforeEach(() => {
			dom = makeDom("<div><p><span></span></p><a></a></div>")[0];
			p = dom.children[0];
			span = p.children[0];
			a = dom.children[1];
		});

		it("leaves unique elements untouched", () => {
			assert.deepEqual(uniqueSort([p, a]), [p, a]);
		});

		it("removes duplicate elements", () => {
			assert.deepEqual(uniqueSort([p, a, p]), [p, a]);
		});

		it("sorts nodes in document order", () => {
			assert.deepEqual(uniqueSort([a, dom, span, p]), [dom, p, span, a]);
		});
	});
});
