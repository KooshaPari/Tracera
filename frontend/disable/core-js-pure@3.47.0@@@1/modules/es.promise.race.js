"use strict";
var $ = require("../internals/export");
var call = require("../internals/function-call");
var aCallable = require("../internals/a-callable");
var newPromiseCapabilityModule = require("../internals/new-promise-capability");
var perform = require("../internals/perform");
var iterate = require("../internals/iterate");
var PROMISE_STATICS_INCORRECT_ITERATION = require("../internals/promise-statics-incorrect-iteration");

// `Promise.race` method
// https://tc39.es/ecma262/#sec-promise.race
$(
	{
		target: "Promise",
		stat: true,
		forced: PROMISE_STATICS_INCORRECT_ITERATION,
	},
	{
		race: function race(iterable) {
			var capability = newPromiseCapabilityModule.f(this);
			var reject = capability.reject;
			var result = perform(() => {
				var $promiseResolve = aCallable(this.resolve);
				iterate(iterable, (promise) => {
					call($promiseResolve, this, promise).then(capability.resolve, reject);
				});
			});
			if (result.error) reject(result.value);
			return capability.promise;
		},
	},
);
