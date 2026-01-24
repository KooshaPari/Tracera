"use strict";
var globalThis = require("../internals/global-this");

module.exports = (CONSTRUCTOR) => globalThis[CONSTRUCTOR].prototype;
