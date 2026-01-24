"use strict";
var createTypedArrayConstructor = require("../internals/typed-array-constructor");

// `Uint16Array` constructor
// https://tc39.es/ecma262/#sec-typedarray-objects
createTypedArrayConstructor(
	"Uint16",
	(init) =>
		function Uint16Array(data, byteOffset, length) {
			return init(this, data, byteOffset, length);
		},
);
