const Reach = require("./reach");

const internals = {};

module.exports = (obj, template, options) =>
	template.replace(/{([^{}]+)}/g, ($0, chain) => {
		const value = Reach(obj, chain, options);
		return value === undefined || value === null ? "" : value;
	});
