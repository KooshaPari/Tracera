"use strict";
var defineProperty = require("../internals/object-define-property");

module.exports = (target, name, descriptor) =>
	defineProperty.f(target, name, descriptor);
