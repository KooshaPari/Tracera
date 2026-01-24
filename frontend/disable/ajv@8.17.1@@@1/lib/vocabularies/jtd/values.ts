import { type Name, not, or } from "../../compile/codegen";
import { alwaysValidSchema, Type } from "../../compile/util";
import type { KeywordCxt } from "../../compile/validate";
import type { CodeKeywordDefinition, SchemaObject } from "../../types";
import { type _JTDTypeError, typeError } from "./error";
import { checkMetadata } from "./metadata";
import { checkNullableObject } from "./nullable";

export type JTDValuesError = _JTDTypeError<"values", "object", SchemaObject>;

const def: CodeKeywordDefinition = {
	keyword: "values",
	schemaType: "object",
	error: typeError("object"),
	code(cxt: KeywordCxt) {
		checkMetadata(cxt);
		const { gen, data, schema, it } = cxt;
		const [valid, cond] = checkNullableObject(cxt, data);
		if (alwaysValidSchema(it, schema)) {
			gen.if(not(or(cond, valid)), () => cxt.error());
		} else {
			gen.if(cond);
			gen.assign(valid, validateMap());
			gen.elseIf(not(valid));
			cxt.error();
			gen.endIf();
		}
		cxt.ok(valid);

		function validateMap(): Name | boolean {
			const _valid = gen.name("valid");
			if (it.allErrors) {
				const validMap = gen.let("valid", true);
				validateValues(() => gen.assign(validMap, false));
				return validMap;
			}
			gen.var(_valid, true);
			validateValues(() => gen.break());
			return _valid;

			function validateValues(notValid: () => void): void {
				gen.forIn("key", data, (key) => {
					cxt.subschema(
						{
							keyword: "values",
							dataProp: key,
							dataPropType: Type.Str,
						},
						_valid,
					);
					gen.if(not(_valid), notValid);
				});
			}
		}
	},
};

export default def;
