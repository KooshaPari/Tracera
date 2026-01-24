import tdz from "./tdz.js";
import temporalUndefined from "./temporalUndefined.js";

function _temporalRef(r, e) {
	return r === temporalUndefined ? tdz(e) : r;
}
export { _temporalRef as default };
