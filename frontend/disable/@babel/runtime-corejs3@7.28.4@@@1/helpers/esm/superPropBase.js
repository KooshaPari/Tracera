import getPrototypeOf from "./getPrototypeOf.js";

function _superPropBase(t, o) {
	for (; !Object.hasOwn(t, o) && null !== (t = getPrototypeOf(t)); );
	return t;
}
export { _superPropBase as default };
