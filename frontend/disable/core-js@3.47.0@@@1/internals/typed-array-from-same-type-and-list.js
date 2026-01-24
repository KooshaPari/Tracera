"use strict";
var arrayFromConstructorAndList = require("../internals/array-from-constructor-and-list");
var getTypedArrayConstructor =
	require("../internals/array-buffer-view-core").getTypedArrayConstructor;

module.exports = (instance, list) =>
	arrayFromConstructorAndList(getTypedArrayConstructor(instance), list);
