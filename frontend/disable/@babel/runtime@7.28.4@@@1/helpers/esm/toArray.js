import arrayWithHoles from "./arrayWithHoles.js";
import iterableToArray from "./iterableToArray.js";
import nonIterableRest from "./nonIterableRest.js";
import unsupportedIterableToArray from "./unsupportedIterableToArray.js";

function _toArray(r) {
	return (
		arrayWithHoles(r) ||
		iterableToArray(r) ||
		unsupportedIterableToArray(r) ||
		nonIterableRest()
	);
}
export { _toArray as default };
