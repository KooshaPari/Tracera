module.exports = (xs, fn) => {
	var res = [];
	for (var i = 0; i < xs.length; i++) {
		var x = fn(xs[i], i);
		if (isArray(x)) res.push.apply(res, x);
		else res.push(x);
	}
	return res;
};

var isArray =
	Array.isArray ||
	((xs) => Object.prototype.toString.call(xs) === "[object Array]");
