"use strict";
var arraySpeciesConstructor = require("../internals/array-species-constructor");

// `ArraySpeciesCreate` abstract operation
// https://tc39.es/ecma262/#sec-arrayspeciescreate
module.exports = (originalArray, length) =>
	new (arraySpeciesConstructor(originalArray))(length === 0 ? 0 : length);
