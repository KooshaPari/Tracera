"use strict";
var DESCRIPTORS = require("../internals/descriptors");
var definePropertyModule = require("../internals/object-define-property");
var createPropertyDescriptor = require("../internals/create-property-descriptor");

module.exports = (object, key, value) => {
	if (DESCRIPTORS)
		definePropertyModule.f(object, key, createPropertyDescriptor(0, value));
	else object[key] = value;
};
