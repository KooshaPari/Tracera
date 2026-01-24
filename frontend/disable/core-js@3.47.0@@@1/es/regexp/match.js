"use strict";
require("../../modules/es.regexp.exec");
require("../../modules/es.string.match");
var call = require("../../internals/function-call");
var wellKnownSymbol = require("../../internals/well-known-symbol");

var MATCH = wellKnownSymbol("match");

module.exports = (it, str) => call(RegExp.prototype[MATCH], it, str);
