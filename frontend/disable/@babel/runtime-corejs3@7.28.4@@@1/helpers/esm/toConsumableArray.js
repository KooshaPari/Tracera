import arrayWithoutHoles from "./arrayWithoutHoles.js";
import iterableToArray from "./iterableToArray.js";
import nonIterableSpread from "./nonIterableSpread.js";
import unsupportedIterableToArray from "./unsupportedIterableToArray.js";

function _toConsumableArray(r) {
	return (
		arrayWithoutHoles(r) ||
		iterableToArray(r) ||
		unsupportedIterableToArray(r) ||
		nonIterableSpread()
	);
}
export { _toConsumableArray as default };
