module.exports = (Promise) => {
	var SomePromiseArray = Promise._SomePromiseArray;
	function any(promises) {
		var ret = new SomePromiseArray(promises);
		var promise = ret.promise();
		ret.setHowMany(1);
		ret.setUnwrap();
		ret.init();
		return promise;
	}

	Promise.any = (promises) => any(promises);

	Promise.prototype.any = function () {
		return any(this);
	};
};
