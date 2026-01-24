import { checkStrictMode } from "../../compile/util";
import type { KeywordCxt } from "../../compile/validate";
import type { CodeKeywordDefinition } from "../../types";

const def: CodeKeywordDefinition = {
	keyword: ["maxContains", "minContains"],
	type: "array",
	schemaType: "number",
	code({ keyword, parentSchema, it }: KeywordCxt) {
		if (parentSchema.contains === undefined) {
			checkStrictMode(it, `"${keyword}" without "contains" is ignored`);
		}
	},
};

export default def;
