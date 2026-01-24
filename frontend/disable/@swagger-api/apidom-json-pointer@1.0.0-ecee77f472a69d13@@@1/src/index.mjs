export {
	ASTTranslator,
	CSTTranslator,
	/**
	 * Compiling
	 */
	compile,
	/**
	 * Escaping
	 */
	escape,
	/**
	 * Grammar
	 */
	Grammar,
	JSONPointerCompileError,
	/**
	 * Errors
	 */
	JSONPointerError,
	JSONPointerEvaluateError,
	JSONPointerIndexError,
	JSONPointerKeyError,
	JSONPointerParseError,
	JSONPointerTypeError,
	/**
	 * Representation
	 */
	JSONString,
	/**
	 * Parsing
	 */
	parse,
	testArrayDash,
	testArrayIndex,
	testArrayLocation,
	/**
	 * Testing
	 */
	testJSONPointer,
	testReferenceToken,
	URIFragmentIdentifier,
	unescape,
	XMLTranslator,
} from "@swaggerexpert/json-pointer";
/**
 * Contextual Evaluation for ApiDOM
 */
export { evaluate } from "@swaggerexpert/json-pointer/evaluate/realms/apidom";
/**
 * Re-export all types
 */
