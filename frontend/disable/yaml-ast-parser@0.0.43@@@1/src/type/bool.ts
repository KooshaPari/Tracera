declare function require(n: string): any;

("use strict");

import { Type } from "../type";

function resolveYamlBoolean(data) {
	if (null === data) {
		return false;
	}

	var max = data.length;

	return (
		(max === 4 && (data === "true" || data === "True" || data === "TRUE")) ||
		(max === 5 && (data === "false" || data === "False" || data === "FALSE"))
	);
}

function constructYamlBoolean(data) {
	return data === "true" || data === "True" || data === "TRUE";
}

function isBoolean(object) {
	return "[object Boolean]" === Object.prototype.toString.call(object);
}

export = new Type("tag:yaml.org,2002:bool", {
	kind: "scalar",
	resolve: resolveYamlBoolean,
	construct: constructYamlBoolean,
	predicate: isBoolean,
	represent: {
		lowercase: (object) => (object ? "true" : "false"),
		uppercase: (object) => (object ? "TRUE" : "FALSE"),
		camelcase: (object) => (object ? "True" : "False"),
	},
	defaultStyle: "lowercase",
});
