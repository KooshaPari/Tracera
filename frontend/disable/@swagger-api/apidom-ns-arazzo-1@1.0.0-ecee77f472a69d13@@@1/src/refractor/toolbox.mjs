import { createNamespace, isStringElement } from "@swagger-api/apidom-core";
import workflowsNamespace from "../namespace.mjs";
import * as workflowsPredicates from "../predicates.mjs";
import * as refractorPredicates from "./predicates.mjs";

const createToolbox = () => {
	const namespace = createNamespace(workflowsNamespace);
	const predicates = {
		...refractorPredicates,
		...workflowsPredicates,
		isStringElement,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
