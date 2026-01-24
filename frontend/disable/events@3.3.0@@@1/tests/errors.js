var assert = require("assert");
var EventEmitter = require("../");

var EE = new EventEmitter();

assert.throws(() => {
	EE.emit("error", "Accepts a string");
}, "Error: Unhandled error. (Accepts a string)");

assert.throws(() => {
	EE.emit("error", { message: "Error!" });
}, "Unhandled error. ([object Object])");
