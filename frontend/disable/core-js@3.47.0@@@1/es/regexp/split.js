"use strict";
require("../../modules/es.regexp.exec");
require("../../modules/es.string.split");
var call = require("../../internals/function-call");
var wellKnownSymbol = require("../../internals/well-known-symbol");

var SPLIT = wellKnownSymbol("split");

module.exports = (it, str, limit) =>
	call(RegExp.prototype[SPLIT], it, str, limit);
