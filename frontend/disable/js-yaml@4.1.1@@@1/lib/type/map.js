var Type = require("../type");

module.exports = new Type("tag:yaml.org,2002:map", {
	kind: "mapping",
	construct: (data) => (data !== null ? data : {}),
});
