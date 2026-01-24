import {
	createNamespace,
	hasElementSourceMap,
	includesClasses,
	isArrayElement,
	isElement,
	isMemberElement,
	isObjectElement,
	isStringElement,
} from "@swagger-api/apidom-core";
import openApi3_0Namespace from "../namespace.mjs";
import * as openApi3_0Predicates from "../predicates.mjs";

/**
 * @public
 */
/**
 * @public
 */
/**
 * @public
 */
const createToolbox = () => {
	const namespace = createNamespace(openApi3_0Namespace);
	const predicates = {
		...openApi3_0Predicates,
		isElement,
		isStringElement,
		isArrayElement,
		isObjectElement,
		isMemberElement,
		includesClasses,
		hasElementSourceMap,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
