"use strict";
// https://github.com/tc39/proposal-async-explicit-resource-management
var call = require("../internals/function-call");
var defineBuiltIn = require("../internals/define-built-in");
var getBuiltIn = require("../internals/get-built-in");
var getMethod = require("../internals/get-method");
var hasOwn = require("../internals/has-own-property");
var wellKnownSymbol = require("../internals/well-known-symbol");
var AsyncIteratorPrototype = require("../internals/async-iterator-prototype");

var ASYNC_DISPOSE = wellKnownSymbol("asyncDispose");
var Promise = getBuiltIn("Promise");

if (!hasOwn(AsyncIteratorPrototype, ASYNC_DISPOSE)) {
	defineBuiltIn(AsyncIteratorPrototype, ASYNC_DISPOSE, function () {
		return new Promise((resolve, reject) => {
			var $return = getMethod(this, "return");
			if ($return) {
				Promise.resolve(call($return, this)).then(() => {
					resolve(undefined);
				}, reject);
			} else resolve(undefined);
		});
	});
}
