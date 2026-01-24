/*!
 * Chai - message composition utility
 * Copyright(c) 2012-2014 Jake Luer <jake@alogicalparadox.com>
 * MIT Licensed
 */

import { flag } from "./flag.js";
import { getActual } from "./getActual.js";
import { objDisplay } from "./objDisplay.js";

/**
 * ### .getMessage(object, message, negateMessage)
 *
 * Construct the error message based on flags
 * and template tags. Template tags will return
 * a stringified inspection of the object referenced.
 *
 * Message template tags:
 * - `#{this}` current asserted object
 * - `#{act}` actual value
 * - `#{exp}` expected value
 *
 * @param {object} obj object (constructed Assertion)
 * @param {IArguments} args chai.Assertion.prototype.assert arguments
 * @returns {string}
 * @namespace Utils
 * @name getMessage
 * @public
 */
export function getMessage(obj, args) {
	const negate = flag(obj, "negate");
	const val = flag(obj, "object");
	const expected = args[3];
	const actual = getActual(obj, args);
	let msg = negate ? args[2] : args[1];
	const flagMsg = flag(obj, "message");

	if (typeof msg === "function") msg = msg();
	msg = msg || "";
	msg = msg
		.replace(/#\{this\}/g, () => objDisplay(val))
		.replace(/#\{act\}/g, () => objDisplay(actual))
		.replace(/#\{exp\}/g, () => objDisplay(expected));

	return flagMsg ? flagMsg + ": " + msg : msg;
}
