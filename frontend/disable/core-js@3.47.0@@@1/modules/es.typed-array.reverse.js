"use strict";
var ArrayBufferViewCore = require("../internals/array-buffer-view-core");

var aTypedArray = ArrayBufferViewCore.aTypedArray;
var exportTypedArrayMethod = ArrayBufferViewCore.exportTypedArrayMethod;
var floor = Math.floor;

// `%TypedArray%.prototype.reverse` method
// https://tc39.es/ecma262/#sec-%typedarray%.prototype.reverse
exportTypedArrayMethod("reverse", function reverse() {
	var length = aTypedArray(this).length;
	var middle = floor(length / 2);
	var index = 0;
	var value;
	while (index < middle) {
		value = this[index];
		this[index++] = this[--length];
		this[length] = value;
	}
	return this;
});
