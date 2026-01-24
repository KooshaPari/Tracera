"use strict";

// https://infra.spec.whatwg.org/#parse-json-from-bytes
exports.parseJSONFromBytes = (bytes) => {
	// https://encoding.spec.whatwg.org/#utf-8-decode
	if (bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
		bytes = bytes.subarray(3);
	}
	const jsonText = bytes.toString("utf-8");

	return JSON.parse(jsonText);
};
