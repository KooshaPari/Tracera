var ElementType = require("domelementtype");
var isTag = (exports.isTag = ElementType.isTag);

exports.testElement = (options, element) => {
	for (var key in options) {
		if (!Object.hasOwn(options, key));
		else if (key === "tag_name") {
			if (!isTag(element) || !options.tag_name(element.name)) {
				return false;
			}
		} else if (key === "tag_type") {
			if (!options.tag_type(element.type)) return false;
		} else if (key === "tag_contains") {
			if (isTag(element) || !options.tag_contains(element.data)) {
				return false;
			}
		} else if (!element.attribs || !options[key](element.attribs[key])) {
			return false;
		}
	}
	return true;
};

var Checks = {
	tag_name: (name) => {
		if (typeof name === "function") {
			return (elem) => isTag(elem) && name(elem.name);
		} else if (name === "*") {
			return isTag;
		} else {
			return (elem) => isTag(elem) && elem.name === name;
		}
	},
	tag_type: (type) => {
		if (typeof type === "function") {
			return (elem) => type(elem.type);
		} else {
			return (elem) => elem.type === type;
		}
	},
	tag_contains: (data) => {
		if (typeof data === "function") {
			return (elem) => !isTag(elem) && data(elem.data);
		} else {
			return (elem) => !isTag(elem) && elem.data === data;
		}
	},
};

function getAttribCheck(attrib, value) {
	if (typeof value === "function") {
		return (elem) => elem.attribs && value(elem.attribs[attrib]);
	} else {
		return (elem) => elem.attribs && elem.attribs[attrib] === value;
	}
}

function combineFuncs(a, b) {
	return (elem) => a(elem) || b(elem);
}

exports.getElements = function (options, element, recurse, limit) {
	var funcs = Object.keys(options).map((key) => {
		var value = options[key];
		return key in Checks ? Checks[key](value) : getAttribCheck(key, value);
	});

	return funcs.length === 0
		? []
		: this.filter(funcs.reduce(combineFuncs), element, recurse, limit);
};

exports.getElementById = function (id, element, recurse) {
	if (!Array.isArray(element)) element = [element];
	return this.findOne(getAttribCheck("id", id), element, recurse !== false);
};

exports.getElementsByTagName = function (name, element, recurse, limit) {
	return this.filter(Checks.tag_name(name), element, recurse, limit);
};

exports.getElementsByTagType = function (type, element, recurse, limit) {
	return this.filter(Checks.tag_type(type), element, recurse, limit);
};
