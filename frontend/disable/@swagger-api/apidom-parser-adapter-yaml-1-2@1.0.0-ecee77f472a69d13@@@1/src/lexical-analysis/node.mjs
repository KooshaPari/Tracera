// @ts-expect-error
import YAMLLanguage from "@tree-sitter-grammars/tree-sitter-yaml";
import Parser from "tree-sitter";

const parser = new Parser();
// @ts-expect-error
parser.setLanguage(YAMLLanguage);

/**
 * Lexical Analysis of source string using TreeSitter.
 * This is Node.js version of TreeSitters Lexical Analysis.
 * @public
 */
const analyze = async (source) => {
	return parser.parse(source);
};
export default analyze;
