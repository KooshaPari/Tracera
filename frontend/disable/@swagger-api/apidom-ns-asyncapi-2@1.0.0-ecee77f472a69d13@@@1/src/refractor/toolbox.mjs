import { createNamespace, isStringElement } from "@swagger-api/apidom-core";
import asyncApi2Namespace from "../namespace.mjs";
import * as asyncApi2Predicates from "../predicates.mjs";

const createToolbox = () => {
	const namespace = createNamespace(asyncApi2Namespace);
	const predicates = {
		...asyncApi2Predicates,
		isStringElement,
	};
	return {
		predicates,
		namespace,
	};
};
export default createToolbox;
