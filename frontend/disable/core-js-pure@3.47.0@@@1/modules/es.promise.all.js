"use strict";
var $ = require("../internals/export");
var call = require("../internals/function-call");
var aCallable = require("../internals/a-callable");
var newPromiseCapabilityModule = require("../internals/new-promise-capability");
var perform = require("../internals/perform");
var iterate = require("../internals/iterate");
var PROMISE_STATICS_INCORRECT_ITERATION = require("../internals/promise-statics-incorrect-iteration");

// `Promise.all` method
// https://tc39.es/ecma262/#sec-promise.all
$(
	{
		target: "Promise",
		stat: true,
		forced: PROMISE_STATICS_INCORRECT_ITERATION,
	},
	{
		all: function all(iterable) {
			var capability = newPromiseCapabilityModule.f(this);
			var resolve = capability.resolve;
			var reject = capability.reject;
			var result = perform(() => {
				var $promiseResolve = aCallable(this.resolve);
				var values = [];
				var counter = 0;
				var remaining = 1;
				iterate(iterable, (promise) => {
					var index = counter++;
					var alreadyCalled = false;
					remaining++;
					call($promiseResolve, this, promise).then((value) => {
						if (alreadyCalled) return;
						alreadyCalled = true;
						values[index] = value;
						--remaining || resolve(values);
					}, reject);
				});
				--remaining || resolve(values);
			});
			if (result.error) reject(result.value);
			return capability.promise;
		},
	},
);
