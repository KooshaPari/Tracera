import { checkStrictMode } from "../../compile/util";
import type { KeywordCxt } from "../../compile/validate";
import type { CodeKeywordDefinition } from "../../types";

const def: CodeKeywordDefinition = {
	keyword: ["then", "else"],
	schemaType: ["object", "boolean"],
	code({ keyword, parentSchema, it }: KeywordCxt) {
		if (parentSchema.if === undefined)
			checkStrictMode(it, `"${keyword}" without "if" is ignored`);
	},
};

export default def;
