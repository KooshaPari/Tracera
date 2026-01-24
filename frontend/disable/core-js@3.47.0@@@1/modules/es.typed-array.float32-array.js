"use strict";
var createTypedArrayConstructor = require("../internals/typed-array-constructor");

// `Float32Array` constructor
// https://tc39.es/ecma262/#sec-typedarray-objects
createTypedArrayConstructor(
	"Float32",
	(init) =>
		function Float32Array(data, byteOffset, length) {
			return init(this, data, byteOffset, length);
		},
);
