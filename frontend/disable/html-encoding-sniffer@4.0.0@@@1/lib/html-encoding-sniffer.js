const whatwgEncoding = require("whatwg-encoding");

// https://html.spec.whatwg.org/#encoding-sniffing-algorithm
module.exports = (
	uint8Array,
	{ transportLayerEncodingLabel, defaultEncoding = "windows-1252" } = {},
) => {
	let encoding = whatwgEncoding.getBOMEncoding(uint8Array);

	if (encoding === null && transportLayerEncodingLabel !== undefined) {
		encoding = whatwgEncoding.labelToName(transportLayerEncodingLabel);
	}

	if (encoding === null) {
		encoding = prescanMetaCharset(uint8Array);
	}

	if (encoding === null) {
		encoding = defaultEncoding;
	}

	return encoding;
};

// https://html.spec.whatwg.org/multipage/syntax.html#prescan-a-byte-stream-to-determine-its-encoding
function prescanMetaCharset(uint8Array) {
	const l = Math.min(uint8Array.byteLength, 1024);
	for (let i = 0; i < l; i++) {
		let c = uint8Array[i];
		if (c === 0x3c) {
			// "<"
			const c1 = uint8Array[i + 1];
			const c2 = uint8Array[i + 2];
			const c3 = uint8Array[i + 3];
			const c4 = uint8Array[i + 4];
			const c5 = uint8Array[i + 5];
			// !-- (comment start)
			if (c1 === 0x21 && c2 === 0x2d && c3 === 0x2d) {
				i += 4;
				for (; i < l; i++) {
					c = uint8Array[i];
					const cMinus1 = uint8Array[i - 1];
					const cMinus2 = uint8Array[i - 2];
					// --> (comment end)
					if (c === 0x3e && cMinus1 === 0x2d && cMinus2 === 0x2d) {
						break;
					}
				}
			} else if (
				(c1 === 0x4d || c1 === 0x6d) &&
				(c2 === 0x45 || c2 === 0x65) &&
				(c3 === 0x54 || c3 === 0x74) &&
				(c4 === 0x41 || c4 === 0x61) &&
				(isSpaceCharacter(c5) || c5 === 0x2f)
			) {
				// "meta" + space or /
				i += 6;
				const attributeList = new Set();
				let gotPragma = false;
				let needPragma = null;
				let charset = null;

				let attrRes;
				do {
					attrRes = getAttribute(uint8Array, i, l);
					if (attrRes.attr && !attributeList.has(attrRes.attr.name)) {
						attributeList.add(attrRes.attr.name);
						if (attrRes.attr.name === "http-equiv") {
							gotPragma = attrRes.attr.value === "content-type";
						} else if (attrRes.attr.name === "content" && !charset) {
							charset = extractCharacterEncodingFromMeta(attrRes.attr.value);
							if (charset !== null) {
								needPragma = true;
							}
						} else if (attrRes.attr.name === "charset") {
							charset = whatwgEncoding.labelToName(attrRes.attr.value);
							needPragma = false;
						}
					}
					i = attrRes.i;
				} while (attrRes.attr);

				if (needPragma === null) {
					continue;
				}
				if (needPragma === true && gotPragma === false) {
					continue;
				}
				if (charset === null) {
					continue;
				}

				if (charset === "UTF-16LE" || charset === "UTF-16BE") {
					charset = "UTF-8";
				}
				if (charset === "x-user-defined") {
					charset = "windows-1252";
				}

				return charset;
			} else if ((c1 >= 0x41 && c1 <= 0x5a) || (c1 >= 0x61 && c1 <= 0x7a)) {
				// a-z or A-Z
				for (i += 2; i < l; i++) {
					c = uint8Array[i];
					// space or >
					if (isSpaceCharacter(c) || c === 0x3e) {
						break;
					}
				}
				let attrRes;
				do {
					attrRes = getAttribute(uint8Array, i, l);
					i = attrRes.i;
				} while (attrRes.attr);
			} else if (c1 === 0x21 || c1 === 0x2f || c1 === 0x3f) {
				// ! or / or ?
				for (i += 2; i < l; i++) {
					c = uint8Array[i];
					// >
					if (c === 0x3e) {
						break;
					}
				}
			}
		}
	}
	return null;
}

// https://html.spec.whatwg.org/multipage/syntax.html#concept-get-attributes-when-sniffing
function getAttribute(uint8Array, i, l) {
	for (; i < l; i++) {
		let c = uint8Array[i];
		// space or /
		if (isSpaceCharacter(c) || c === 0x2f) {
			continue;
		}
		// ">"
		if (c === 0x3e) {
			break;
		}
		let name = "";
		let value = "";
		nameLoop: for (; i < l; i++) {
			c = uint8Array[i];
			// "="
			if (c === 0x3d && name !== "") {
				i++;
				break;
			}
			// space
			if (isSpaceCharacter(c)) {
				for (i++; i < l; i++) {
					c = uint8Array[i];
					// space
					if (isSpaceCharacter(c)) {
						continue;
					}
					// not "="
					if (c !== 0x3d) {
						return { attr: { name, value }, i };
					}

					i++;
					break nameLoop;
				}
				break;
			}
			// / or >
			if (c === 0x2f || c === 0x3e) {
				return { attr: { name, value }, i };
			}
			// A-Z
			if (c >= 0x41 && c <= 0x5a) {
				name += String.fromCharCode(c + 0x20); // lowercase
			} else {
				name += String.fromCharCode(c);
			}
		}
		c = uint8Array[i];
		// space
		if (isSpaceCharacter(c)) {
			for (i++; i < l; i++) {
				c = uint8Array[i];
				// space
				if (isSpaceCharacter(c)) {
				} else {
					break;
				}
			}
		}
		// " or '
		if (c === 0x22 || c === 0x27) {
			const quote = c;
			for (i++; i < l; i++) {
				c = uint8Array[i];

				if (c === quote) {
					i++;
					return { attr: { name, value }, i };
				}

				// A-Z
				if (c >= 0x41 && c <= 0x5a) {
					value += String.fromCharCode(c + 0x20); // lowercase
				} else {
					value += String.fromCharCode(c);
				}
			}
		}

		// >
		if (c === 0x3e) {
			return { attr: { name, value }, i };
		}

		// A-Z
		if (c >= 0x41 && c <= 0x5a) {
			value += String.fromCharCode(c + 0x20); // lowercase
		} else {
			value += String.fromCharCode(c);
		}

		for (i++; i < l; i++) {
			c = uint8Array[i];

			// space or >
			if (isSpaceCharacter(c) || c === 0x3e) {
				return { attr: { name, value }, i };
			}

			// A-Z
			if (c >= 0x41 && c <= 0x5a) {
				value += String.fromCharCode(c + 0x20); // lowercase
			} else {
				value += String.fromCharCode(c);
			}
		}
	}
	return { i };
}

function extractCharacterEncodingFromMeta(string) {
	let position = 0;

	while (true) {
		const indexOfCharset = string.substring(position).search(/charset/iu);

		if (indexOfCharset === -1) {
			return null;
		}
		let subPosition = position + indexOfCharset + "charset".length;

		while (isSpaceCharacter(string[subPosition].charCodeAt(0))) {
			++subPosition;
		}

		if (string[subPosition] !== "=") {
			position = subPosition - 1;
			continue;
		}

		++subPosition;

		while (isSpaceCharacter(string[subPosition].charCodeAt(0))) {
			++subPosition;
		}

		position = subPosition;
		break;
	}

	if (string[position] === '"' || string[position] === "'") {
		const nextIndex = string.indexOf(string[position], position + 1);

		if (nextIndex !== -1) {
			return whatwgEncoding.labelToName(
				string.substring(position + 1, nextIndex),
			);
		}

		// It is an unmatched quotation mark
		return null;
	}

	if (string.length === position + 1) {
		return null;
	}

	const indexOfASCIIWhitespaceOrSemicolon = string
		.substring(position + 1)
		.search(/\x09|\x0A|\x0C|\x0D|\x20|;/u);
	const end =
		indexOfASCIIWhitespaceOrSemicolon === -1
			? string.length
			: position + indexOfASCIIWhitespaceOrSemicolon + 1;

	return whatwgEncoding.labelToName(string.substring(position, end));
}

function isSpaceCharacter(c) {
	return c === 0x09 || c === 0x0a || c === 0x0c || c === 0x0d || c === 0x20;
}
