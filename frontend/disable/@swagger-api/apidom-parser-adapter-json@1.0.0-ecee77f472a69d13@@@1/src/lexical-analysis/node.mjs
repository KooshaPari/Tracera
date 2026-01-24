import Parser from "tree-sitter";
// @ts-expect-error
import JSONLanguage from "tree-sitter-json";

const parser = new Parser();
parser.setLanguage(JSONLanguage);

/**
 * Lexical Analysis of source string using TreeSitter.
 * This is Node.js version of TreeSitters Lexical Analysis.
 * @public
 */
const analyze = async (source) => {
	return parser.parse(source);
};
export default analyze;
