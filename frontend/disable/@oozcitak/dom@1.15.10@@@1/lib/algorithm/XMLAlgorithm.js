Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Determines if the given string is valid for a `"Name"` construct.
 *
 * @param name - name string to test
 */
function xml_isName(name) {
	for (var i = 0; i < name.length; i++) {
		var n = name.charCodeAt(i);
		// NameStartChar
		if (
			(n >= 97 && n <= 122) || // [a-z]
			(n >= 65 && n <= 90) || // [A-Z]
			n === 58 ||
			n === 95 || // ':' or '_'
			(n >= 0xc0 && n <= 0xd6) ||
			(n >= 0xd8 && n <= 0xf6) ||
			(n >= 0xf8 && n <= 0x2ff) ||
			(n >= 0x370 && n <= 0x37d) ||
			(n >= 0x37f && n <= 0x1fff) ||
			(n >= 0x200c && n <= 0x200d) ||
			(n >= 0x2070 && n <= 0x218f) ||
			(n >= 0x2c00 && n <= 0x2fef) ||
			(n >= 0x3001 && n <= 0xd7ff) ||
			(n >= 0xf900 && n <= 0xfdcf) ||
			(n >= 0xfdf0 && n <= 0xfffd)
		) {
			continue;
		} else if (
			i !== 0 &&
			(n === 45 ||
				n === 46 || // '-' or '.'
				(n >= 48 && n <= 57) || // [0-9]
				n === 0xb7 ||
				(n >= 0x0300 && n <= 0x036f) ||
				(n >= 0x203f && n <= 0x2040))
		) {
			continue;
		}
		if (n >= 0xd800 && n <= 0xdbff && i < name.length - 1) {
			var n2 = name.charCodeAt(i + 1);
			if (n2 >= 0xdc00 && n2 <= 0xdfff) {
				n = (n - 0xd800) * 0x400 + n2 - 0xdc00 + 0x10000;
				i++;
				if (n >= 0x10000 && n <= 0xeffff) {
					continue;
				}
			}
		}
		return false;
	}
	return true;
}
exports.xml_isName = xml_isName;
/**
 * Determines if the given string is valid for a `"QName"` construct.
 *
 * @param name - name string to test
 */
function xml_isQName(name) {
	var colonFound = false;
	for (var i = 0; i < name.length; i++) {
		var n = name.charCodeAt(i);
		// NameStartChar
		if (
			(n >= 97 && n <= 122) || // [a-z]
			(n >= 65 && n <= 90) || // [A-Z]
			n === 95 || // '_'
			(n >= 0xc0 && n <= 0xd6) ||
			(n >= 0xd8 && n <= 0xf6) ||
			(n >= 0xf8 && n <= 0x2ff) ||
			(n >= 0x370 && n <= 0x37d) ||
			(n >= 0x37f && n <= 0x1fff) ||
			(n >= 0x200c && n <= 0x200d) ||
			(n >= 0x2070 && n <= 0x218f) ||
			(n >= 0x2c00 && n <= 0x2fef) ||
			(n >= 0x3001 && n <= 0xd7ff) ||
			(n >= 0xf900 && n <= 0xfdcf) ||
			(n >= 0xfdf0 && n <= 0xfffd)
		) {
			continue;
		} else if (
			i !== 0 &&
			(n === 45 ||
				n === 46 || // '-' or '.'
				(n >= 48 && n <= 57) || // [0-9]
				n === 0xb7 ||
				(n >= 0x0300 && n <= 0x036f) ||
				(n >= 0x203f && n <= 0x2040))
		) {
			continue;
		} else if (i !== 0 && n === 58) {
			// :
			if (colonFound) return false; // multiple colons in qname
			if (i === name.length - 1) return false; // colon at the end of qname
			colonFound = true;
			continue;
		}
		if (n >= 0xd800 && n <= 0xdbff && i < name.length - 1) {
			var n2 = name.charCodeAt(i + 1);
			if (n2 >= 0xdc00 && n2 <= 0xdfff) {
				n = (n - 0xd800) * 0x400 + n2 - 0xdc00 + 0x10000;
				i++;
				if (n >= 0x10000 && n <= 0xeffff) {
					continue;
				}
			}
		}
		return false;
	}
	return true;
}
exports.xml_isQName = xml_isQName;
/**
 * Determines if the given string contains legal characters.
 *
 * @param chars - sequence of characters to test
 */
function xml_isLegalChar(chars) {
	for (var i = 0; i < chars.length; i++) {
		var n = chars.charCodeAt(i);
		// #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
		if (
			n === 0x9 ||
			n === 0xa ||
			n === 0xd ||
			(n >= 0x20 && n <= 0xd7ff) ||
			(n >= 0xe000 && n <= 0xfffd)
		) {
			continue;
		}
		if (n >= 0xd800 && n <= 0xdbff && i < chars.length - 1) {
			var n2 = chars.charCodeAt(i + 1);
			if (n2 >= 0xdc00 && n2 <= 0xdfff) {
				n = (n - 0xd800) * 0x400 + n2 - 0xdc00 + 0x10000;
				i++;
				if (n >= 0x10000 && n <= 0x10ffff) {
					continue;
				}
			}
		}
		return false;
	}
	return true;
}
exports.xml_isLegalChar = xml_isLegalChar;
/**
 * Determines if the given string contains legal characters for a public
 * identifier.
 *
 * @param chars - sequence of characters to test
 */
function xml_isPubidChar(chars) {
	for (var i = 0; i < chars.length; i++) {
		// PubId chars are all in the ASCII range, no need to check surrogates
		var n = chars.charCodeAt(i);
		// #x20 | #xD | #xA | [a-zA-Z0-9] | [-'()+,./:=?;!*#@$_%]
		if (
			(n >= 97 && n <= 122) || // [a-z]
			(n >= 65 && n <= 90) || // [A-Z]
			(n >= 39 && n <= 59) || // ['()*+,-./] | [0-9] | [:;]
			n === 0x20 ||
			n === 0xd ||
			n === 0xa || // #x20 | #xD | #xA
			(n >= 35 && n <= 37) || // [#$%]
			n === 33 || // !
			n === 61 ||
			n === 63 ||
			n === 64 ||
			n === 95
		) {
		} else {
			return false;
		}
	}
	return true;
}
exports.xml_isPubidChar = xml_isPubidChar;
//# sourceMappingURL=XMLAlgorithm.js.map
