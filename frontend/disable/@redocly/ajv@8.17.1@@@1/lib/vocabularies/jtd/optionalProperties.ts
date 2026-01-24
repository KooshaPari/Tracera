import type { KeywordCxt } from "../../compile/validate";
import type { CodeKeywordDefinition } from "../../types";
import { error, validateProperties } from "./properties";

const def: CodeKeywordDefinition = {
	keyword: "optionalProperties",
	schemaType: "object",
	error,
	code(cxt: KeywordCxt) {
		if (cxt.parentSchema.properties) return;
		validateProperties(cxt);
	},
};

export default def;
