import { createNamespace, isStringElement } from "@swagger-api/apidom-core";
import jsonSchemaDraft4Namespace from "../namespace.mjs";
import * as jsonSchemaDraft4Predicates from "../predicates.mjs";

const createToolbox = () => {
	const namespace = createNamespace(jsonSchemaDraft4Namespace);
	const predicates = {
		...jsonSchemaDraft4Predicates,
		isStringElement,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
