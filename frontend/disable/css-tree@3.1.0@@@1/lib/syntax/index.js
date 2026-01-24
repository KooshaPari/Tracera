import lexerConfig from "./config/lexer.js";
import parserConfig from "./config/parser.js";
import walkerConfig from "./config/walker.js";
import createSyntax from "./create.js";

export default createSyntax({
	...lexerConfig,
	...parserConfig,
	...walkerConfig,
});
