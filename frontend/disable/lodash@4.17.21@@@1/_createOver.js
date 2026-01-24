var apply = require("./_apply"),
	arrayMap = require("./_arrayMap"),
	baseIteratee = require("./_baseIteratee"),
	baseRest = require("./_baseRest"),
	baseUnary = require("./_baseUnary"),
	flatRest = require("./_flatRest");

/**
 * Creates a function like `_.over`.
 *
 * @private
 * @param {Function} arrayFunc The function to iterate over iteratees.
 * @returns {Function} Returns the new over function.
 */
function createOver(arrayFunc) {
	return flatRest((iteratees) => {
		iteratees = arrayMap(iteratees, baseUnary(baseIteratee));
		return baseRest(function (args) {
			return arrayFunc(iteratees, (iteratee) => apply(iteratee, this, args));
		});
	});
}

module.exports = createOver;
