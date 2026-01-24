const internals = {};

module.exports = (string) => {
	// Escape ^$.*+-?=!:|\/()[]{},

	return string.replace(/[\^$.*+\-?=!:|\\/()[\]{},]/g, "\\$&");
};
