"use strict";
var isCallable = require("../internals/is-callable");

module.exports = (it) => (typeof it == "object" ? it !== null : isCallable(it));
