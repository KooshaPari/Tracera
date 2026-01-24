var assert = require("assert"),
	path = require("path"),
	entities = require("../");

describe("Encode->decode test", () => {
	var testcases = [
		{
			input: "asdf & ÿ ü '",
			xml: "asdf &amp; &#xFF; &#xFC; &apos;",
			html: "asdf &amp; &yuml; &uuml; &apos;",
		},
		{
			input: "&#38;",
			xml: "&amp;#38;",
			html: "&amp;&num;38&semi;",
		},
	];
	testcases.forEach((tc) => {
		var encodedXML = entities.encodeXML(tc.input);
		it("should XML encode " + tc.input, () => {
			assert.equal(encodedXML, tc.xml);
		});
		it("should default to XML encode " + tc.input, () => {
			assert.equal(entities.encode(tc.input), tc.xml);
		});
		it("should XML decode " + encodedXML, () => {
			assert.equal(entities.decodeXML(encodedXML), tc.input);
		});
		it("should default to XML encode " + encodedXML, () => {
			assert.equal(entities.decode(encodedXML), tc.input);
		});
		it("should default strict to XML encode " + encodedXML, () => {
			assert.equal(entities.decodeStrict(encodedXML), tc.input);
		});

		var encodedHTML5 = entities.encodeHTML5(tc.input);
		it("should HTML5 encode " + tc.input, () => {
			assert.equal(encodedHTML5, tc.html);
		});
		it("should HTML5 decode " + encodedHTML5, () => {
			assert.equal(entities.decodeHTML(encodedHTML5), tc.input);
		});
	});

	it("should encode data URIs (issue 16)", () => {
		var data =
			"data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAALAAABAAEAAAIBRAA7";
		assert.equal(entities.decode(entities.encode(data)), data);
	});
});

describe("Decode test", () => {
	var testcases = [
		{ input: "&amp;amp;", output: "&amp;" },
		{ input: "&amp;#38;", output: "&#38;" },
		{ input: "&amp;#x26;", output: "&#x26;" },
		{ input: "&amp;#X26;", output: "&#X26;" },
		{ input: "&#38;#38;", output: "&#38;" },
		{ input: "&#x26;#38;", output: "&#38;" },
		{ input: "&#X26;#38;", output: "&#38;" },
		{ input: "&#x3a;", output: ":" },
		{ input: "&#x3A;", output: ":" },
		{ input: "&#X3a;", output: ":" },
		{ input: "&#X3A;", output: ":" },
	];
	testcases.forEach((tc) => {
		it("should XML decode " + tc.input, () => {
			assert.equal(entities.decodeXML(tc.input), tc.output);
		});
		it("should HTML4 decode " + tc.input, () => {
			assert.equal(entities.decodeHTML(tc.input), tc.output);
		});
		it("should HTML5 decode " + tc.input, () => {
			assert.equal(entities.decodeHTML(tc.input), tc.output);
		});
	});
});

var levels = ["xml", "entities"];

describe("Documents", () => {
	levels
		.map((n) => path.join("..", "maps", n))
		.map(require)
		.forEach((doc, i) => {
			describe("Decode", () => {
				it(levels[i], () => {
					Object.keys(doc).forEach((e) => {
						for (var l = i; l < levels.length; l++) {
							assert.equal(entities.decode("&" + e + ";", l), doc[e]);
						}
					});
				});
			});

			describe("Decode strict", () => {
				it(levels[i], () => {
					Object.keys(doc).forEach((e) => {
						for (var l = i; l < levels.length; l++) {
							assert.equal(entities.decodeStrict("&" + e + ";", l), doc[e]);
						}
					});
				});
			});

			describe("Encode", () => {
				it(levels[i], () => {
					Object.keys(doc).forEach((e) => {
						for (var l = i; l < levels.length; l++) {
							assert.equal(
								entities.decode(entities.encode(doc[e], l), l),
								doc[e],
							);
						}
					});
				});
			});
		});

	var legacy = require("../maps/legacy.json");

	describe("Legacy", () => {
		it("should decode", runLegacy);
	});

	function runLegacy() {
		Object.keys(legacy).forEach((e) => {
			assert.equal(entities.decodeHTML("&" + e), legacy[e]);
		});
	}
});

var astral = {
	"1D306": "\uD834\uDF06",
	"1D11E": "\uD834\uDD1E",
};

var astralSpecial = {
	80: "\u20AC",
	110000: "\uFFFD",
};

describe("Astral entities", () => {
	Object.keys(astral).forEach((c) => {
		it("should decode " + astral[c], () => {
			assert.equal(entities.decode("&#x" + c + ";"), astral[c]);
		});

		it("should encode " + astral[c], () => {
			assert.equal(entities.encode(astral[c]), "&#x" + c + ";");
		});

		it("should escape " + astral[c], () => {
			assert.equal(entities.escape(astral[c]), "&#x" + c + ";");
		});
	});

	Object.keys(astralSpecial).forEach((c) => {
		it("special should decode \\u" + c, () => {
			assert.equal(entities.decode("&#x" + c + ";"), astralSpecial[c]);
		});
	});
});

describe("Escape", () => {
	it("should always decode ASCII chars", () => {
		for (var i = 0; i < 0x7f; i++) {
			var c = String.fromCharCode(i);
			assert.equal(entities.decodeXML(entities.escape(c)), c);
		}
	});
});
