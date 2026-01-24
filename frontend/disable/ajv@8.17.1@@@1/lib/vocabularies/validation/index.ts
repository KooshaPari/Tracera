import type { ErrorObject, Vocabulary } from "../../types";
import constKeyword, { type ConstError } from "./const";
import enumKeyword, { type EnumError } from "./enum";
import limitItems from "./limitItems";
import limitLength from "./limitLength";
import limitNumber, { type LimitNumberError } from "./limitNumber";
import limitProperties from "./limitProperties";
import multipleOf, { type MultipleOfError } from "./multipleOf";
import pattern, { type PatternError } from "./pattern";
import required, { type RequiredError } from "./required";
import uniqueItems, { type UniqueItemsError } from "./uniqueItems";

const validation: Vocabulary = [
	// number
	limitNumber,
	multipleOf,
	// string
	limitLength,
	pattern,
	// object
	limitProperties,
	required,
	// array
	limitItems,
	uniqueItems,
	// any
	{ keyword: "type", schemaType: ["string", "array"] },
	{ keyword: "nullable", schemaType: "boolean" },
	constKeyword,
	enumKeyword,
];

export default validation;

type LimitError = ErrorObject<
	| "maxItems"
	| "minItems"
	| "minProperties"
	| "maxProperties"
	| "minLength"
	| "maxLength",
	{ limit: number },
	number | { $data: string }
>;

export type ValidationKeywordError =
	| LimitError
	| LimitNumberError
	| MultipleOfError
	| PatternError
	| RequiredError
	| UniqueItemsError
	| ConstError
	| EnumError;
