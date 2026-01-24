const styfn = {};

styfn.appendFromJson = function (json) {
	for (let i = 0; i < json.length; i++) {
		const context = json[i];
		const selector = context.selector;
		const props = context.style || context.css;
		const names = Object.keys(props);

		this.selector(selector); // apply selector

		for (let j = 0; j < names.length; j++) {
			const name = names[j];
			const value = props[name];

			this.css(name, value); // apply property
		}
	}

	return this;
};

// accessible cy.style() function
styfn.fromJson = function (json) {
	this.resetToDefault();
	this.appendFromJson(json);

	return this;
};

// get json from cy.style() api
styfn.json = function () {
	const json = [];

	for (let i = this.defaultLength; i < this.length; i++) {
		const cxt = this[i];
		const selector = cxt.selector;
		const props = cxt.properties;
		const css = {};

		for (let j = 0; j < props.length; j++) {
			const prop = props[j];
			css[prop.name] = prop.strValue;
		}

		json.push({
			selector: !selector ? "core" : selector.toString(),
			style: css,
		});
	}

	return json;
};

export default styfn;
