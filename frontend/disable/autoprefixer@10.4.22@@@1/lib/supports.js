const featureQueries = require("caniuse-lite/data/features/css-featurequeries.js");
const feature = require("caniuse-lite/dist/unpacker/feature");
const { parse } = require("postcss");

const brackets = require("./brackets");
const Browsers = require("./browsers");
const utils = require("./utils");
const Value = require("./value");

const data = feature(featureQueries);

const supported = [];
for (const browser in data.stats) {
	const versions = data.stats[browser];
	for (const version in versions) {
		const support = versions[version];
		if (/y/.test(support)) {
			supported.push(browser + " " + version);
		}
	}
}

class Supports {
	constructor(Prefixes, all) {
		this.Prefixes = Prefixes;
		this.all = all;
	}

	/**
	 * Add prefixes
	 */
	add(nodes, all) {
		return nodes.map((i) => {
			if (this.isProp(i)) {
				const prefixed = this.prefixed(i[0]);
				if (prefixed.length > 1) {
					return this.convert(prefixed);
				}

				return i;
			}

			if (typeof i === "object") {
				return this.add(i, all);
			}

			return i;
		});
	}

	/**
	 * Clean brackets with one child
	 */
	cleanBrackets(nodes) {
		return nodes.map((i) => {
			if (typeof i !== "object") {
				return i;
			}

			if (i.length === 1 && typeof i[0] === "object") {
				return this.cleanBrackets(i[0]);
			}

			return this.cleanBrackets(i);
		});
	}

	/**
	 * Add " or " between properties and convert it to brackets format
	 */
	convert(progress) {
		const result = [""];
		for (const i of progress) {
			result.push([`${i.prop}: ${i.value}`]);
			result.push(" or ");
		}
		result[result.length - 1] = "";
		return result;
	}

	/**
	 * Check global options
	 */
	disabled(node) {
		if (!this.all.options.grid) {
			if (node.prop === "display" && node.value.includes("grid")) {
				return true;
			}
			if (node.prop.includes("grid") || node.prop === "justify-items") {
				return true;
			}
		}

		if (this.all.options.flexbox === false) {
			if (node.prop === "display" && node.value.includes("flex")) {
				return true;
			}
			const other = [
				"order",
				"justify-content",
				"align-items",
				"align-content",
			];
			if (node.prop.includes("flex") || other.includes(node.prop)) {
				return true;
			}
		}

		return false;
	}

	/**
	 * Return true if prefixed property has no unprefixed
	 */
	isHack(all, unprefixed) {
		const check = new RegExp(`(\\(|\\s)${utils.escapeRegexp(unprefixed)}:`);
		return !check.test(all);
	}

	/**
	 * Return true if brackets node is "not" word
	 */
	isNot(node) {
		return typeof node === "string" && /not\s*/i.test(node);
	}

	/**
	 * Return true if brackets node is "or" word
	 */
	isOr(node) {
		return typeof node === "string" && /\s*or\s*/i.test(node);
	}

	/**
	 * Return true if brackets node is (prop: value)
	 */
	isProp(node) {
		return (
			typeof node === "object" &&
			node.length === 1 &&
			typeof node[0] === "string"
		);
	}

	/**
	 * Compress value functions into a string nodes
	 */
	normalize(nodes) {
		if (typeof nodes !== "object") {
			return nodes;
		}

		nodes = nodes.filter((i) => i !== "");

		if (typeof nodes[0] === "string") {
			const firstNode = nodes[0].trim();

			if (
				firstNode.includes(":") ||
				firstNode === "selector" ||
				firstNode === "not selector"
			) {
				return [brackets.stringify(nodes)];
			}
		}
		return nodes.map((i) => this.normalize(i));
	}

	/**
	 * Parse string into declaration property and value
	 */
	parse(str) {
		const parts = str.split(":");
		const prop = parts[0];
		let value = parts[1];
		if (!value) value = "";
		return [prop.trim(), value.trim()];
	}

	/**
	 * Return array of Declaration with all necessary prefixes
	 */
	prefixed(str) {
		const rule = this.virtual(str);
		if (this.disabled(rule.first)) {
			return rule.nodes;
		}

		const result = { warn: () => null };

		const prefixer = this.prefixer().add[rule.first.prop];
		prefixer && prefixer.process && prefixer.process(rule.first, result);

		for (const decl of rule.nodes) {
			for (const value of this.prefixer().values("add", rule.first.prop)) {
				value.process(decl);
			}
			Value.save(this.all, decl);
		}

		return rule.nodes;
	}

	/**
	 * Return prefixer only with @supports supported browsers
	 */
	prefixer() {
		if (this.prefixerCache) {
			return this.prefixerCache;
		}

		const filtered = this.all.browsers.selected.filter((i) => {
			return supported.includes(i);
		});

		const browsers = new Browsers(
			this.all.browsers.data,
			filtered,
			this.all.options,
		);
		this.prefixerCache = new this.Prefixes(
			this.all.data,
			browsers,
			this.all.options,
		);
		return this.prefixerCache;
	}

	/**
	 * Add prefixed declaration
	 */
	process(rule) {
		let ast = brackets.parse(rule.params);
		ast = this.normalize(ast);
		ast = this.remove(ast, rule.params);
		ast = this.add(ast, rule.params);
		ast = this.cleanBrackets(ast);
		rule.params = brackets.stringify(ast);
	}

	/**
	 * Remove all unnecessary prefixes
	 */
	remove(nodes, all) {
		let i = 0;
		while (i < nodes.length) {
			if (
				!this.isNot(nodes[i - 1]) &&
				this.isProp(nodes[i]) &&
				this.isOr(nodes[i + 1])
			) {
				if (this.toRemove(nodes[i][0], all)) {
					nodes.splice(i, 2);
					continue;
				}

				i += 2;
				continue;
			}

			if (typeof nodes[i] === "object") {
				nodes[i] = this.remove(nodes[i], all);
			}

			i += 1;
		}
		return nodes;
	}

	/**
	 * Return true if we need to remove node
	 */
	toRemove(str, all) {
		const [prop, value] = this.parse(str);
		const unprefixed = this.all.unprefixed(prop);

		const cleaner = this.all.cleaner();

		if (
			cleaner.remove[prop] &&
			cleaner.remove[prop].remove &&
			!this.isHack(all, unprefixed)
		) {
			return true;
		}

		for (const checker of cleaner.values("remove", unprefixed)) {
			if (checker.check(value)) {
				return true;
			}
		}

		return false;
	}

	/**
	 * Create virtual rule to process it by prefixer
	 */
	virtual(str) {
		const [prop, value] = this.parse(str);
		const rule = parse("a{}").first;
		rule.append({ prop, raws: { before: "" }, value });
		return rule;
	}
}

module.exports = Supports;
