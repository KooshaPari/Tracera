import {
	isObjectElement,
	isStringElement,
	toValue,
} from "@swagger-api/apidom-core";
import { startsWith } from "ramda";

/**
 * @public
 */

/**
 * @public
 */
export const isSwaggerExtension = (element) => {
	return isStringElement(element.key) && startsWith("x-", toValue(element.key));
};

/**
 * @public
 */
export const isReferenceLikeElement = (element) => {
	return isObjectElement(element) && element.hasKey("$ref");
};
