import toPrimitive from "./toPrimitive.js";
import _typeof from "./typeof.js";

function toPropertyKey(t) {
	var i = toPrimitive(t, "string");
	return "symbol" == _typeof(i) ? i : i + "";
}
export { toPropertyKey as default };
