import arrayWithHoles from "./arrayWithHoles.js";
import iterableToArrayLimit from "./iterableToArrayLimit.js";
import nonIterableRest from "./nonIterableRest.js";
import unsupportedIterableToArray from "./unsupportedIterableToArray.js";

function _slicedToArray(r, e) {
	return (
		arrayWithHoles(r) ||
		iterableToArrayLimit(r, e) ||
		unsupportedIterableToArray(r, e) ||
		nonIterableRest()
	);
}
export { _slicedToArray as default };
