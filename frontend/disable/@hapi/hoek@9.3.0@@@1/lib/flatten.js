const internals = {};

module.exports = internals.flatten = (array, target) => {
	const result = target || [];

	for (const entry of array) {
		if (Array.isArray(entry)) {
			internals.flatten(entry, result);
		} else {
			result.push(entry);
		}
	}

	return result;
};
