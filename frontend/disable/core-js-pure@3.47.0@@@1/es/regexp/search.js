"use strict";
require("../../modules/es.regexp.exec");
require("../../modules/es.string.search");
var call = require("../../internals/function-call");
var wellKnownSymbol = require("../../internals/well-known-symbol");

var SEARCH = wellKnownSymbol("search");

module.exports = (it, str) => call(RegExp.prototype[SEARCH], it, str);
