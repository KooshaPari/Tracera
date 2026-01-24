import { createNamespace, isStringElement } from "@swagger-api/apidom-core";
import jsonSchema201909Namespace from "../namespace.mjs";
import * as jsonSchema201909Predicates from "../predicates.mjs";

const createToolbox = () => {
	const namespace = createNamespace(jsonSchema201909Namespace);
	const predicates = {
		...jsonSchema201909Predicates,
		isStringElement,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
