const browserslist = require("browserslist");
const { agents } = require("caniuse-lite/dist/unpacker/agents");

const utils = require("./utils");

class Browsers {
	constructor(data, requirements, options, browserslistOpts) {
		this.data = data;
		this.options = options || {};
		this.browserslistOpts = browserslistOpts || {};
		this.selected = this.parse(requirements);
	}

	/**
	 * Return all prefixes for default browser data
	 */
	static prefixes() {
		if (Browsers.prefixesCache) {
			return Browsers.prefixesCache;
		}

		Browsers.prefixesCache = [];
		for (const name in agents) {
			Browsers.prefixesCache.push(`-${agents[name].prefix}-`);
		}

		Browsers.prefixesCache = utils
			.uniq(Browsers.prefixesCache)
			.sort((a, b) => b.length - a.length);

		return Browsers.prefixesCache;
	}

	/**
	 * Check is value contain any possible prefix
	 */
	static withPrefix(value) {
		if (!Browsers.prefixesRegexp) {
			Browsers.prefixesRegexp = new RegExp(Browsers.prefixes().join("|"));
		}

		return Browsers.prefixesRegexp.test(value);
	}

	/**
	 * Is browser is selected by requirements
	 */
	isSelected(browser) {
		return this.selected.includes(browser);
	}

	/**
	 * Return browsers selected by requirements
	 */
	parse(requirements) {
		const opts = {};
		for (const i in this.browserslistOpts) {
			opts[i] = this.browserslistOpts[i];
		}
		opts.path = this.options.from;
		return browserslist(requirements, opts);
	}

	/**
	 * Return prefix for selected browser
	 */
	prefix(browser) {
		const [name, version] = browser.split(" ");
		const data = this.data[name];

		let prefix = data.prefix_exceptions && data.prefix_exceptions[version];
		if (!prefix) {
			prefix = data.prefix;
		}
		return `-${prefix}-`;
	}
}

module.exports = Browsers;
