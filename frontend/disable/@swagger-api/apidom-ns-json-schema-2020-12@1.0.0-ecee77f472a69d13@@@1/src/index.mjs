export {
	isArrayElement,
	isBooleanElement,
	isElement,
	isLinkElement,
	isMemberElement,
	isNullElement,
	isNumberElement,
	isObjectElement,
	isRefElement,
	isStringElement,
} from "@swagger-api/apidom-core";
export {
	$defsVisitor,
	$refVisitor,
	$vocabularyVisitor,
	AllOfVisitor,
	AlternatingVisitor,
	AnyOfVisitor,
	DependentRequiredVisitor,
	DependentSchemasVisitor,
	FallbackVisitor,
	FixedFieldsVisitor,
	ItemsVisitor,
	MapVisitor,
	OneOfVisitor,
	ParentSchemaAwareVisitor,
	PatternedFieldsVisitor,
	PatternPropertiesVisitor,
	PropertiesVisitor,
	SpecificationVisitor,
	Visitor,
} from "@swagger-api/apidom-ns-json-schema-2019-09";
export {
	default as mediaTypes,
	JSONSchema202012MediaTypes,
} from "./media-types.mjs";
// eslint-disable-next-line no-restricted-exports
export { default } from "./namespace.mjs";
export {
	isJSONSchemaElement,
	isLinkDescriptionElement,
} from "./predicates.mjs";
export { createRefractor, default as refract } from "./refractor/index.mjs";
export { default as refractorPluginReplaceEmptyElement } from "./refractor/plugins/replace-empty-element.mjs";
/**
 * JSON Schema 2020-12 specification elements.
 */
export {
	JSONSchemaElement,
	LinkDescriptionElement,
} from "./refractor/registration.mjs";
export { default as specificationObj } from "./refractor/specification.mjs";
export { default as JSONSchemaVisitor } from "./refractor/visitors/json-schema/index.mjs";
export { default as LinkDescriptionVisitor } from "./refractor/visitors/json-schema/link-description/index.mjs";
export { default as PrefixItemsVisitor } from "./refractor/visitors/json-schema/PrefixItemsVisitor.mjs";
