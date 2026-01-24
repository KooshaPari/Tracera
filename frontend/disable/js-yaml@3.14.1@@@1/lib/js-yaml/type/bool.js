var Type = require("../type");

function resolveYamlBoolean(data) {
	if (data === null) return false;

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
	return Object.prototype.toString.call(object) === "[object Boolean]";
}

module.exports = new Type("tag:yaml.org,2002:bool", {
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
