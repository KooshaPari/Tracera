"use strict";
// TODO: Remove from `core-js@4`
var getBuiltIn = require("../internals/get-built-in");
var aConstructor = require("../internals/a-constructor");
var arrayFromAsync = require("../internals/array-from-async");
var ArrayBufferViewCore = require("../internals/array-buffer-view-core");
var arrayFromConstructorAndList = require("../internals/array-from-constructor-and-list");

var aTypedArrayConstructor = ArrayBufferViewCore.aTypedArrayConstructor;
var exportTypedArrayStaticMethod =
	ArrayBufferViewCore.exportTypedArrayStaticMethod;

// `%TypedArray%.fromAsync` method
// https://github.com/tc39/proposal-array-from-async
exportTypedArrayStaticMethod(
	"fromAsync",
	function fromAsync(
		asyncItems /* , mapfn = undefined, thisArg = undefined */,
	) {
		var argumentsLength = arguments.length;
		var mapfn = argumentsLength > 1 ? arguments[1] : undefined;
		var thisArg = argumentsLength > 2 ? arguments[2] : undefined;
		return new (getBuiltIn("Promise"))((resolve) => {
			aConstructor(this);
			resolve(arrayFromAsync(asyncItems, mapfn, thisArg));
		}).then((list) =>
			arrayFromConstructorAndList(aTypedArrayConstructor(this), list),
		);
	},
	true,
);
