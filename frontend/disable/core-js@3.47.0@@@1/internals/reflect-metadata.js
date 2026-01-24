"use strict";
// TODO: in core-js@4, move /modules/ dependencies to public entries for better optimization by tools like `preset-env`
require("../modules/es.map");
require("../modules/es.weak-map");
var getBuiltIn = require("../internals/get-built-in");
var uncurryThis = require("../internals/function-uncurry-this");
var shared = require("../internals/shared");

var Map = getBuiltIn("Map");
var WeakMap = getBuiltIn("WeakMap");
var push = uncurryThis([].push);

var metadata = shared("metadata");
var store = metadata.store || (metadata.store = new WeakMap());

var getOrCreateMetadataMap = (target, targetKey, create) => {
	var targetMetadata = store.get(target);
	if (!targetMetadata) {
		if (!create) return;
		store.set(target, (targetMetadata = new Map()));
	}
	var keyMetadata = targetMetadata.get(targetKey);
	if (!keyMetadata) {
		if (!create) return;
		targetMetadata.set(targetKey, (keyMetadata = new Map()));
	}
	return keyMetadata;
};

var ordinaryHasOwnMetadata = (MetadataKey, O, P) => {
	var metadataMap = getOrCreateMetadataMap(O, P, false);
	return metadataMap === undefined ? false : metadataMap.has(MetadataKey);
};

var ordinaryGetOwnMetadata = (MetadataKey, O, P) => {
	var metadataMap = getOrCreateMetadataMap(O, P, false);
	return metadataMap === undefined ? undefined : metadataMap.get(MetadataKey);
};

var ordinaryDefineOwnMetadata = (MetadataKey, MetadataValue, O, P) => {
	getOrCreateMetadataMap(O, P, true).set(MetadataKey, MetadataValue);
};

var ordinaryOwnMetadataKeys = (target, targetKey) => {
	var metadataMap = getOrCreateMetadataMap(target, targetKey, false);
	var keys = [];
	if (metadataMap)
		metadataMap.forEach((_, key) => {
			push(keys, key);
		});
	return keys;
};

var toMetadataKey = (it) =>
	it === undefined || typeof it == "symbol" ? it : String(it);

module.exports = {
	store: store,
	getMap: getOrCreateMetadataMap,
	has: ordinaryHasOwnMetadata,
	get: ordinaryGetOwnMetadata,
	set: ordinaryDefineOwnMetadata,
	keys: ordinaryOwnMetadataKeys,
	toKey: toMetadataKey,
};
