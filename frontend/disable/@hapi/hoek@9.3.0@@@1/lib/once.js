const internals = {
	wrapped: Symbol("wrapped"),
};

module.exports = (method) => {
	if (method[internals.wrapped]) {
		return method;
	}

	let once = false;
	const wrappedFn = (...args) => {
		if (!once) {
			once = true;
			method(...args);
		}
	};

	wrappedFn[internals.wrapped] = true;
	return wrappedFn;
};
