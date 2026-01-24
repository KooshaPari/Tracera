import type { Vocabulary } from "../../types";
import discriminator, { type JTDDiscriminatorError } from "./discriminator";
import elements, { type JTDElementsError } from "./elements";
import enumKeyword, { type JTDEnumError } from "./enum";
import metadata from "./metadata";
import optionalProperties from "./optionalProperties";
import properties, { type JTDPropertiesError } from "./properties";
import refKeyword from "./ref";
import typeKeyword, { type JTDTypeError } from "./type";
import union from "./union";
import values, { type JTDValuesError } from "./values";

const jtdVocabulary: Vocabulary = [
	"definitions",
	refKeyword,
	typeKeyword,
	enumKeyword,
	elements,
	properties,
	optionalProperties,
	discriminator,
	values,
	union,
	metadata,
	{ keyword: "additionalProperties", schemaType: "boolean" },
	{ keyword: "nullable", schemaType: "boolean" },
];

export default jtdVocabulary;

export type JTDErrorObject =
	| JTDTypeError
	| JTDEnumError
	| JTDElementsError
	| JTDPropertiesError
	| JTDDiscriminatorError
	| JTDValuesError;
