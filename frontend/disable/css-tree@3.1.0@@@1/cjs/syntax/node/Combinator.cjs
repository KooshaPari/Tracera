"use strict";

const types = require("../../tokenizer/types.cjs");

const PLUSSIGN = 0x002b; // U+002B PLUS SIGN (+)
const SOLIDUS = 0x002f; // U+002F SOLIDUS (/)
const GREATERTHANSIGN = 0x003e; // U+003E GREATER-THAN SIGN (>)
const TILDE = 0x007e; // U+007E TILDE (~)

const name = "Combinator";
const structure = {
	name: String,
};

// + | > | ~ | /deep/
function parse() {
	const start = this.tokenStart;
	let name;

	switch (this.tokenType) {
		case types.WhiteSpace:
			name = " ";
			break;

		case types.Delim:
			switch (this.charCodeAt(this.tokenStart)) {
				case GREATERTHANSIGN:
				case PLUSSIGN:
				case TILDE:
					this.next();
					break;

				case SOLIDUS:
					this.next();
					this.eatIdent("deep");
					this.eatDelim(SOLIDUS);
					break;

				default:
					this.error("Combinator is expected");
			}

			name = this.substrToCursor(start);
			break;
	}

	return {
		type: "Combinator",
		loc: this.getLocation(start, this.tokenStart),
		name,
	};
}

function generate(node) {
	this.tokenize(node.name);
}

exports.generate = generate;
exports.name = name;
exports.parse = parse;
exports.structure = structure;
