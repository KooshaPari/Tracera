"use strict";
var shared = require("../internals/shared");
var uid = require("../internals/uid");

var keys = shared("keys");

module.exports = (key) => keys[key] || (keys[key] = uid(key));
