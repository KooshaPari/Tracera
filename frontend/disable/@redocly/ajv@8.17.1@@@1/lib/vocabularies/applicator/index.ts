import type { ErrorNoParams, Vocabulary } from "../../types";
import additionalItems, { type AdditionalItemsError } from "./additionalItems";
import additionalProperties, {
	type AdditionalPropertiesError,
} from "./additionalProperties";
import allOf from "./allOf";
import anyOf, { type AnyOfError } from "./anyOf";
import contains, { type ContainsError } from "./contains";
import dependencies, { type DependenciesError } from "./dependencies";
import ifKeyword, { type IfKeywordError } from "./if";
import items from "./items";
import items2020, { type ItemsError } from "./items2020";
import notKeyword, { type NotKeywordError } from "./not";
import oneOf, { type OneOfError } from "./oneOf";
import patternProperties from "./patternProperties";
import prefixItems from "./prefixItems";
import properties from "./properties";
import propertyNames, { type PropertyNamesError } from "./propertyNames";
import thenElse from "./thenElse";

export default function getApplicator(draft2020 = false): Vocabulary {
	const applicator = [
		// any
		notKeyword,
		anyOf,
		oneOf,
		allOf,
		ifKeyword,
		thenElse,
		// object
		propertyNames,
		additionalProperties,
		dependencies,
		properties,
		patternProperties,
	];
	// array
	if (draft2020) applicator.push(prefixItems, items2020);
	else applicator.push(additionalItems, items);
	applicator.push(contains);
	return applicator;
}

export type ApplicatorKeywordError =
	| ErrorNoParams<"false schema">
	| AdditionalItemsError
	| ItemsError
	| ContainsError
	| AdditionalPropertiesError
	| DependenciesError
	| IfKeywordError
	| AnyOfError
	| OneOfError
	| NotKeywordError
	| PropertyNamesError;
