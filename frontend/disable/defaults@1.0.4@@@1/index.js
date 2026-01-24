var clone = require("clone");

module.exports = (options, defaults) => {
	options = options || {};

	Object.keys(defaults).forEach((key) => {
		if (typeof options[key] === "undefined") {
			options[key] = clone(defaults[key]);
		}
	});

	return options;
};
