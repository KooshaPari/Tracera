import getPrototypeOf from "./getPrototypeOf.js";
import set from "./set.js";

function _superPropSet(t, e, o, r, p, f) {
	return set(getPrototypeOf(f ? t.prototype : t), e, o, r, p);
}
export { _superPropSet as default };
