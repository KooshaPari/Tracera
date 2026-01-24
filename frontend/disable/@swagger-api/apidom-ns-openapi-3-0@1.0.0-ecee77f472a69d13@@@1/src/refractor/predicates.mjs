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
export const isReferenceLikeElement = (element) => {
	return isObjectElement(element) && element.hasKey("$ref");
};

/**
 * @public
 */
export const isServerLikeElement = isObjectElement;

/**
 * @public
 */
export const isTagLikeElement = isObjectElement;

/**
 * @public
 */
export const isOpenApiExtension = (element) => {
	// @ts-expect-error
	return isStringElement(element.key) && startsWith("x-", toValue(element.key));
};
