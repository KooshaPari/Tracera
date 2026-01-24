"use strict";
var uncurryThis = require("../internals/function-uncurry-this");

var toString = uncurryThis({}.toString);
var stringSlice = uncurryThis("".slice);

module.exports = (it) => stringSlice(toString(it), 8, -1);
