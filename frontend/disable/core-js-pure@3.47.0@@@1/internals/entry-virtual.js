"use strict";
var path = require("../internals/path");

module.exports = (CONSTRUCTOR) => path[CONSTRUCTOR + "Prototype"];
