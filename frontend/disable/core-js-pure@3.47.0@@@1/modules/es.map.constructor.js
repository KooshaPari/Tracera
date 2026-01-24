"use strict";
var collection = require("../internals/collection");
var collectionStrong = require("../internals/collection-strong");

// `Map` constructor
// https://tc39.es/ecma262/#sec-map-objects
collection(
	"Map",
	(init) =>
		function Map() {
			return init(this, arguments.length ? arguments[0] : undefined);
		},
	collectionStrong,
);
