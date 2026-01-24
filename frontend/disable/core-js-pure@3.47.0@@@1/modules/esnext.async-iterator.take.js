"use strict";
var $ = require("../internals/export");
var call = require("../internals/function-call");
var anObject = require("../internals/an-object");
var getIteratorDirect = require("../internals/get-iterator-direct");
var notANaN = require("../internals/not-a-nan");
var toPositiveInteger = require("../internals/to-positive-integer");
var createAsyncIteratorProxy = require("../internals/async-iterator-create-proxy");
var createIterResultObject = require("../internals/create-iter-result-object");

var AsyncIteratorProxy = createAsyncIteratorProxy(function (Promise) {
	var iterator = this.iterator;
	var returnMethod;

	if (!this.remaining--) {
		var resultDone = createIterResultObject(undefined, true);
		this.done = true;
		returnMethod = iterator["return"];
		if (returnMethod !== undefined) {
			return Promise.resolve(call(returnMethod, iterator, undefined)).then(
				() => resultDone,
			);
		}
		return resultDone;
	}
	return Promise.resolve(call(this.next, iterator))
		.then((step) => {
			if (anObject(step).done) {
				this.done = true;
				return createIterResultObject(undefined, true);
			}
			return createIterResultObject(step.value, false);
		})
		.then(null, (error) => {
			this.done = true;
			throw error;
		});
});

// `AsyncIterator.prototype.take` method
// https://github.com/tc39/proposal-async-iterator-helpers
$(
	{ target: "AsyncIterator", proto: true, real: true, forced: true },
	{
		take: function take(limit) {
			anObject(this);
			var remaining = toPositiveInteger(notANaN(+limit));
			return new AsyncIteratorProxy(getIteratorDirect(this), {
				remaining: remaining,
			});
		},
	},
);
