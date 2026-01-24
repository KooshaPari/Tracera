import { createNamespace, isStringElement } from "@swagger-api/apidom-core";
import apiDesignSystemNamespace from "../namespace.mjs";
import * as apiDesignSystemsPredicates from "../predicates.mjs";

const createToolbox = () => {
	const namespace = createNamespace(apiDesignSystemNamespace);
	const predicates = {
		...apiDesignSystemsPredicates,
		isStringElement,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
