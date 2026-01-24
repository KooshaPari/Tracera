module.exports = {
	prefix(prop) {
		const match = prop.match(/^(-\w+-)/);
		if (match) {
			return match[0];
		}

		return "";
	},

	unprefixed(prop) {
		return prop.replace(/^-\w+-/, "");
	},
};
