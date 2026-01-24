module.exports = (Promise, INTERNAL) => {
	var PromiseMap = Promise.map;

	Promise.prototype.filter = function (fn, options) {
		return PromiseMap(this, fn, options, INTERNAL);
	};

	Promise.filter = (promises, fn, options) =>
		PromiseMap(promises, fn, options, INTERNAL);
};
