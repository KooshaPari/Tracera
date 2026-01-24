import type { CodeKeywordDefinition, ErrorObject } from "../../types";
import {
	type DependenciesErrorParams,
	error,
	type PropertyDependencies,
	validatePropertyDeps,
} from "../applicator/dependencies";

export type DependentRequiredError = ErrorObject<
	"dependentRequired",
	DependenciesErrorParams,
	PropertyDependencies
>;

const def: CodeKeywordDefinition = {
	keyword: "dependentRequired",
	type: "object",
	schemaType: "object",
	error,
	code: (cxt) => validatePropertyDeps(cxt),
};

export default def;
