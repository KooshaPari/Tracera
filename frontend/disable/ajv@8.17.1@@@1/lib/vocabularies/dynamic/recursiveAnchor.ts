import { checkStrictMode } from "../../compile/util";
import type { CodeKeywordDefinition } from "../../types";
import { dynamicAnchor } from "./dynamicAnchor";

const def: CodeKeywordDefinition = {
	keyword: "$recursiveAnchor",
	schemaType: "boolean",
	code(cxt) {
		if (cxt.schema) dynamicAnchor(cxt, "");
		else checkStrictMode(cxt.it, "$recursiveAnchor: false is ignored");
	},
};

export default def;
