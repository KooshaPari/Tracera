"use strict";
var fails = require("../internals/fails");

// check the existence of a method, lowercase
// of a tag and escaping quotes in arguments
module.exports = (METHOD_NAME) =>
	fails(() => {
		var test = ""[METHOD_NAME]('"');
		return test !== test.toLowerCase() || test.split('"').length > 3;
	});
