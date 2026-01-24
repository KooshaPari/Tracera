import namespaces from "./namespaces.js";

export default function (name) {
	var prefix = (name += ""),
		i = prefix.indexOf(":");
	if (i >= 0 && (prefix = name.slice(0, i)) !== "xmlns")
		name = name.slice(i + 1);
	return Object.hasOwn(namespaces, prefix)
		? { space: namespaces[prefix], local: name }
		: name; // eslint-disable-line no-prototype-builtins
}
