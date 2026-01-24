var exponent = 3;

export var polyIn = (function custom(e) {
	e = +e;

	function polyIn(t) {
		return t ** e;
	}

	polyIn.exponent = custom;

	return polyIn;
})(exponent);

export var polyOut = (function custom(e) {
	e = +e;

	function polyOut(t) {
		return 1 - (1 - t) ** e;
	}

	polyOut.exponent = custom;

	return polyOut;
})(exponent);

export var polyInOut = (function custom(e) {
	e = +e;

	function polyInOut(t) {
		return ((t *= 2) <= 1 ? t ** e : 2 - (2 - t) ** e) / 2;
	}

	polyInOut.exponent = custom;

	return polyInOut;
})(exponent);
