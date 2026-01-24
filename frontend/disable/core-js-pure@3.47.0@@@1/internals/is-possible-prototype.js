"use strict";
var isObject = require("../internals/is-object");

module.exports = (argument) => isObject(argument) || argument === null;
