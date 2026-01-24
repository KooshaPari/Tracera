"use strict";
var fails = require("../internals/fails");

module.exports = (METHOD_NAME, argument) => {
	var method = [][METHOD_NAME];
	return (
		!!method &&
		fails(() => {
			// eslint-disable-next-line no-useless-call -- required for testing
			method.call(null, argument || (() => 1), 1);
		})
	);
};
