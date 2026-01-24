"use strict";
var DESCRIPTORS = require("../internals/descriptors");
var definePropertyModule = require("../internals/object-define-property");
var createPropertyDescriptor = require("../internals/create-property-descriptor");

module.exports = DESCRIPTORS
	? (object, key, value) =>
			definePropertyModule.f(object, key, createPropertyDescriptor(1, value))
	: (object, key, value) => {
			object[key] = value;
			return object;
		};
