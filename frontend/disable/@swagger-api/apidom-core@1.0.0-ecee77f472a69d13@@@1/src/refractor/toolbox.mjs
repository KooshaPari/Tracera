import defaultNamespaceInstance from "../namespace.mjs";
import * as basePredicates from "../predicates/index.mjs";

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
	const predicates = {
		...basePredicates,
	};
	return {
		predicates,
		namespace: defaultNamespaceInstance,
	};
};
export default createToolbox;
