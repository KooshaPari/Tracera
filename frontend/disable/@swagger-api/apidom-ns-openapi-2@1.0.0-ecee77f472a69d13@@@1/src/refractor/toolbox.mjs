import { createNamespace, isStringElement } from "@swagger-api/apidom-core";
import openApi2Namespace from "../namespace.mjs";
import * as openApi2Predicates from "../predicates.mjs";
import * as refractorPredicates from "./predicates.mjs";

const createToolbox = () => {
	const namespace = createNamespace(openApi2Namespace);
	const predicates = {
		...refractorPredicates,
		...openApi2Predicates,
		isStringElement,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
