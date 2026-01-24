var getChildren = (exports.getChildren = (elem) => elem.children);

var getParent = (exports.getParent = (elem) => elem.parent);

exports.getSiblings = (elem) => {
	var parent = getParent(elem);
	return parent ? getChildren(parent) : [elem];
};

exports.getAttributeValue = (elem, name) => elem.attribs && elem.attribs[name];

exports.hasAttrib = (elem, name) =>
	!!elem.attribs && hasOwnProperty.call(elem.attribs, name);

exports.getName = (elem) => elem.name;
