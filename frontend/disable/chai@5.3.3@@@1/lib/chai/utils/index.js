/*!
 * chai
 * Copyright(c) 2011 Jake Luer <jake@alogicalparadox.com>
 * MIT Licensed
 */

// Dependencies that are used for multiple exports are required here only once
import * as checkError from "check-error";

// test utility
export { test } from "./test.js";

// type utility
import { type } from "./type-detect.js";
export { type };

// Deep equal utility
export { default as eql } from "deep-eql";
// Deep path info
export { getPathInfo, hasProperty } from "pathval";
// expectTypes utility
export { expectTypes } from "./expectTypes.js";
// Flag utility
export { flag } from "./flag.js";
// actual utility
export { getActual } from "./getActual.js";
// message utility
export { getMessage } from "./getMessage.js";
// Inspect util
export { inspect } from "./inspect.js";
// Object Display util
export { objDisplay } from "./objDisplay.js";
// Flag transferring utility
export { transferFlags } from "./transferFlags.js";

/**
 * Function name
 *
 * @param {Function} fn
 * @returns {string}
 */
export function getName(fn) {
	return fn.name;
}

// Add a chainable method
export { addChainableMethod } from "./addChainableMethod.js";

// add Method
export { addMethod } from "./addMethod.js";
// add Property
export { addProperty } from "./addProperty.js";
// Compare by inspect method
export { compareByInspect } from "./compareByInspect.js";
// Get own enumerable properties method
export { getOwnEnumerableProperties } from "./getOwnEnumerableProperties.js";
// Get own enumerable property symbols method
export { getOwnEnumerablePropertySymbols } from "./getOwnEnumerablePropertySymbols.js";
// Overwrite chainable method
export { overwriteChainableMethod } from "./overwriteChainableMethod.js";
// overwrite Method
export { overwriteMethod } from "./overwriteMethod.js";
// overwrite Property
export { overwriteProperty } from "./overwriteProperty.js";

// Checks error against a given set of criteria
export { checkError };

// addLengthGuard util
export { addLengthGuard } from "./addLengthGuard.js";
// getOperator method
export { getOperator } from "./getOperator.js";
// isNaN method
export { isNaN } from "./isNaN.js";
// isProxyEnabled helper
export { isProxyEnabled } from "./isProxyEnabled.js";
// Proxify util
export { proxify } from "./proxify.js";

/**
 * Determines if an object is a `RegExp`
 * This is used since `instanceof` will not work in virtual contexts
 *
 * @param {*} obj Object to test
 * @returns {boolean}
 */
export function isRegExp(obj) {
	return Object.prototype.toString.call(obj) === "[object RegExp]";
}

/**
 * Determines if an object is numeric or not
 *
 * @param {unknown} obj Object to test
 * @returns {boolean}
 */
export function isNumeric(obj) {
	return ["Number", "BigInt"].includes(type(obj));
}
