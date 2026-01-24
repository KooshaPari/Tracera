"use strict";
var getIterator = require("../internals/get-iterator");
var getIteratorDirect = require("../internals/get-iterator-direct");

module.exports = (argument) => getIteratorDirect(getIterator(argument));
