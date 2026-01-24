var defineProperties = require("define-properties");

var implementation = require("./implementation");
var getPolyfill = require("./polyfill");
var shim = require("./shim");

var polyfill = getPolyfill();

var getGlobal = () => polyfill;

defineProperties(getGlobal, {
	getPolyfill: getPolyfill,
	implementation: implementation,
	shim: shim,
});

module.exports = getGlobal;
