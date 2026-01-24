"use strict";
var call = require("../internals/function-call");
var aCallable = require("../internals/a-callable");
var anObject = require("../internals/an-object");
var isObject = require("../internals/is-object");
var getIteratorDirect = require("../internals/get-iterator-direct");
var createAsyncIteratorProxy = require("../internals/async-iterator-create-proxy");
var createIterResultObject = require("../internals/create-iter-result-object");
var closeAsyncIteration = require("../internals/async-iterator-close");

var AsyncIteratorProxy = createAsyncIteratorProxy(function (Promise) {
	var iterator = this.iterator;
	var mapper = this.mapper;

	return new Promise((resolve, reject) => {
		var doneAndReject = (error) => {
			this.done = true;
			reject(error);
		};

		var ifAbruptCloseAsyncIterator = (error) => {
			closeAsyncIteration(iterator, doneAndReject, error, doneAndReject);
		};

		Promise.resolve(anObject(call(this.next, iterator))).then((step) => {
			try {
				if (anObject(step).done) {
					this.done = true;
					resolve(createIterResultObject(undefined, true));
				} else {
					var value = step.value;
					try {
						var result = mapper(value, this.counter++);

						var handler = (mapped) => {
							resolve(createIterResultObject(mapped, false));
						};

						if (isObject(result))
							Promise.resolve(result).then(handler, ifAbruptCloseAsyncIterator);
						else handler(result);
					} catch (error2) {
						ifAbruptCloseAsyncIterator(error2);
					}
				}
			} catch (error) {
				doneAndReject(error);
			}
		}, doneAndReject);
	});
});

// `AsyncIterator.prototype.map` method
// https://github.com/tc39/proposal-async-iterator-helpers
module.exports = function map(mapper) {
	anObject(this);
	aCallable(mapper);
	return new AsyncIteratorProxy(getIteratorDirect(this), {
		mapper: mapper,
	});
};
