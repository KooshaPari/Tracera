var next = require("./next.js");

module.exports = function maybe(cb, promise) {
	if (cb) {
		promise.then(
			(result) => {
				next(() => {
					cb(null, result);
				});
			},
			(err) => {
				next(() => {
					cb(err);
				});
			},
		);
		return undefined;
	} else {
		return promise;
	}
};
