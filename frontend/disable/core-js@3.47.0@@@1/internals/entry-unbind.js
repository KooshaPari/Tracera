"use strict";
var globalThis = require("../internals/global-this");
var uncurryThis = require("../internals/function-uncurry-this");

module.exports = (CONSTRUCTOR, METHOD) =>
	uncurryThis(globalThis[CONSTRUCTOR].prototype[METHOD]);
