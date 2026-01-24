"use strict";
require("../../modules/es.regexp.exec");
require("../../modules/es.string.replace");
var call = require("../../internals/function-call");
var wellKnownSymbol = require("../../internals/well-known-symbol");

var REPLACE = wellKnownSymbol("replace");

module.exports = (it, str, replacer) =>
	call(RegExp.prototype[REPLACE], it, str, replacer);
