const internals = {};

module.exports = (...args) => {
	try {
		return JSON.stringify(...args);
	} catch (err) {
		return "[Cannot display object: " + err.message + "]";
	}
};
