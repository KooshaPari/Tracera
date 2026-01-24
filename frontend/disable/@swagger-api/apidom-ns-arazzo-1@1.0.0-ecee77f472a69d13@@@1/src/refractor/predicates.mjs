import {
	isObjectElement,
	isStringElement,
	toValue,
} from "@swagger-api/apidom-core";
import { startsWith } from "ramda";
/**
 * @public
 */
export const isArazzoSpecificationExtension = (element) => {
	return isStringElement(element.key) && startsWith("x-", toValue(element.key));
};
export const isReferenceLikeElement = (element) => {
	return isObjectElement(element) && element.hasKey("$ref");
};
