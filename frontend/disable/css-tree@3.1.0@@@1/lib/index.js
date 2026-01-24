import syntax from "./syntax/index.js";

export * as definitionSyntax from "./definition-syntax/index.js";
export { Lexer } from "./lexer/Lexer.js";
export { default as createSyntax } from "./syntax/create.js";
export {
	OffsetToLocation,
	TokenStream,
	tokenNames,
	tokenTypes,
} from "./tokenizer/index.js";
export { clone } from "./utils/clone.js";
export * as ident from "./utils/ident.js";
export { List } from "./utils/List.js";
export * from "./utils/names.js";
export * as string from "./utils/string.js";
export * as url from "./utils/url.js";
export * from "./version.js";
export const {
	tokenize,
	parse,
	generate,
	lexer,
	createLexer,

	walk,
	find,
	findLast,
	findAll,

	toPlainObject,
	fromPlainObject,

	fork,
} = syntax;
