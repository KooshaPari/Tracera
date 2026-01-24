import {
	refract as baseRefract,
	dereference,
	dispatchRefractorPlugins,
	visit,
} from "@swagger-api/apidom-core";
import { path } from "ramda";
import { getNodeType, keyMap } from "../traversal/visitor.mjs";
import specification from "./specification.mjs";
import createToolbox from "./toolbox.mjs";

/**
 * @public
 */
const refract = (
	value,
	{
		specPath = ["visitors", "document", "objects", "JSONSchema", "$visitor"],
		plugins = [],
		specificationObj = specification,
	} = {},
) => {
	const element = baseRefract(value);
	const resolvedSpec = dereference(specificationObj);

	/**
	 * This is where generic ApiDOM becomes semantic (namespace applied).
	 * We don't allow consumers to hook into this translation.
	 * Though we allow consumers to define their onw plugins on already transformed ApiDOM.
	 */
	const RootVisitorClass = path(specPath, resolvedSpec);
	const rootVisitor = new RootVisitorClass({
		specObj: resolvedSpec,
	});
	visit(element, rootVisitor);

	/**
	 * Run plugins only when necessary.
	 * Running plugins visitors means extra single traversal === performance hit.
	 */
	return dispatchRefractorPlugins(rootVisitor.element, plugins, {
		toolboxCreator: createToolbox,
		visitorOptions: {
			keyMap,
			nodeTypeGetter: getNodeType,
		},
	});
};

/**
 * @public
 */
export const createRefractor =
	(specPath) =>
	(value, options = {}) =>
		refract(value, {
			specPath,
			...options,
		});
export default refract;
