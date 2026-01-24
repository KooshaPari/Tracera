"use strict";
var createTypedArrayConstructor = require("../internals/typed-array-constructor");

// `Float64Array` constructor
// https://tc39.es/ecma262/#sec-typedarray-objects
createTypedArrayConstructor(
	"Float64",
	(init) =>
		function Float64Array(data, byteOffset, length) {
			return init(this, data, byteOffset, length);
		},
);
