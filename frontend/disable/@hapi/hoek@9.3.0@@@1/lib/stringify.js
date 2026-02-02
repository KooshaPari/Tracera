const internals = {};

module.exports = (...args) => {
	try {
		return JSON.stringify(...args);
	} catch (_err) {
		return "[Cannot display object: " + err.message + "]";
	}
};
