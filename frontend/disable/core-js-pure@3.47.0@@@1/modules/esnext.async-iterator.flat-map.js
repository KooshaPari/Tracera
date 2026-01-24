"use strict";
var $ = require("../internals/export");
var call = require("../internals/function-call");
var aCallable = require("../internals/a-callable");
var anObject = require("../internals/an-object");
var isObject = require("../internals/is-object");
var getIteratorDirect = require("../internals/get-iterator-direct");
var createAsyncIteratorProxy = require("../internals/async-iterator-create-proxy");
var createIterResultObject = require("../internals/create-iter-result-object");
var getAsyncIteratorFlattenable = require("../internals/get-async-iterator-flattenable");
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

		var outerLoop = () => {
			try {
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
									try {
										this.inner = getAsyncIteratorFlattenable(mapped);
										innerLoop();
									} catch (error4) {
										ifAbruptCloseAsyncIterator(error4);
									}
								};

								if (isObject(result))
									Promise.resolve(result).then(
										handler,
										ifAbruptCloseAsyncIterator,
									);
								else handler(result);
							} catch (error3) {
								ifAbruptCloseAsyncIterator(error3);
							}
						}
					} catch (error2) {
						doneAndReject(error2);
					}
				}, doneAndReject);
			} catch (error) {
				doneAndReject(error);
			}
		};

		var innerLoop = () => {
			var inner = this.inner;
			if (inner) {
				try {
					Promise.resolve(anObject(call(inner.next, inner.iterator))).then(
						(result) => {
							try {
								if (anObject(result).done) {
									this.inner = null;
									outerLoop();
								} else resolve(createIterResultObject(result.value, false));
							} catch (error1) {
								ifAbruptCloseAsyncIterator(error1);
							}
						},
						ifAbruptCloseAsyncIterator,
					);
				} catch (error) {
					ifAbruptCloseAsyncIterator(error);
				}
			} else outerLoop();
		};

		innerLoop();
	});
});

// `AsyncIterator.prototype.flatMap` method
// https://github.com/tc39/proposal-async-iterator-helpers
$(
	{ target: "AsyncIterator", proto: true, real: true, forced: true },
	{
		flatMap: function flatMap(mapper) {
			anObject(this);
			aCallable(mapper);
			return new AsyncIteratorProxy(getIteratorDirect(this), {
				mapper: mapper,
				inner: null,
			});
		},
	},
);
