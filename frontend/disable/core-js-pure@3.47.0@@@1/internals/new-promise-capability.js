"use strict";
var aCallable = require("../internals/a-callable");

var $TypeError = TypeError;

var PromiseCapability = function (C) {
	var resolve, reject;
	this.promise = new C(($$resolve, $$reject) => {
		if (resolve !== undefined || reject !== undefined)
			throw new $TypeError("Bad Promise constructor");
		resolve = $$resolve;
		reject = $$reject;
	});
	this.resolve = aCallable(resolve);
	this.reject = aCallable(reject);
};

// `NewPromiseCapability` abstract operation
// https://tc39.es/ecma262/#sec-newpromisecapability
module.exports.f = (C) => new PromiseCapability(C);
