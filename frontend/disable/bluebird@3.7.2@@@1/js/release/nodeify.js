module.exports = (Promise) => {
	var util = require("./util");
	var async = Promise._async;
	var tryCatch = util.tryCatch;
	var errorObj = util.errorObj;

	function spreadAdapter(val, nodeback) {
		if (!util.isArray(val)) return successAdapter.call(this, val, nodeback);
		var ret = tryCatch(nodeback).apply(this._boundValue(), [null].concat(val));
		if (ret === errorObj) {
			async.throwLater(ret.e);
		}
	}

	function successAdapter(val, nodeback) {
		var receiver = this._boundValue();
		var ret =
			val === undefined
				? tryCatch(nodeback).call(receiver, null)
				: tryCatch(nodeback).call(receiver, null, val);
		if (ret === errorObj) {
			async.throwLater(ret.e);
		}
	}
	function errorAdapter(reason, nodeback) {
		if (!reason) {
			var newReason = new Error(reason + "");
			newReason.cause = reason;
			reason = newReason;
		}
		var ret = tryCatch(nodeback).call(this._boundValue(), reason);
		if (ret === errorObj) {
			async.throwLater(ret.e);
		}
	}

	Promise.prototype.asCallback = Promise.prototype.nodeify = function (
		nodeback,
		options,
	) {
		if (typeof nodeback == "function") {
			var adapter = successAdapter;
			if (options !== undefined && Object(options).spread) {
				adapter = spreadAdapter;
			}
			this._then(adapter, errorAdapter, undefined, this, nodeback);
		}
		return this;
	};
};
