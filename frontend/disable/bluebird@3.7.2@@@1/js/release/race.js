module.exports = (Promise, INTERNAL, tryConvertToPromise, apiRejection) => {
	var util = require("./util");

	var raceLater = (promise) => promise.then((array) => race(array, promise));

	function race(promises, parent) {
		var maybePromise = tryConvertToPromise(promises);

		if (maybePromise instanceof Promise) {
			return raceLater(maybePromise);
		} else {
			promises = util.asArray(promises);
			if (promises === null)
				return apiRejection(
					"expecting an array or an iterable object but got " +
						util.classString(promises),
				);
		}

		var ret = new Promise(INTERNAL);
		if (parent !== undefined) {
			ret._propagateFrom(parent, 3);
		}
		var fulfill = ret._fulfill;
		var reject = ret._reject;
		for (var i = 0, len = promises.length; i < len; ++i) {
			var val = promises[i];

			if (val === undefined && !(i in promises)) {
				continue;
			}

			Promise.cast(val)._then(fulfill, reject, undefined, ret, null);
		}
		return ret;
	}

	Promise.race = (promises) => race(promises, undefined);

	Promise.prototype.race = function () {
		return race(this, undefined);
	};
};
