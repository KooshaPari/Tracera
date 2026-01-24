import { _, type Code, type Name, nil, not } from "../../compile/codegen";
import type { KeywordCxt } from "../../compile/validate";

export function checkNullable(
	{ gen, data, parentSchema }: KeywordCxt,
	cond: Code = nil,
): [Name, Code] {
	const valid = gen.name("valid");
	if (parentSchema.nullable) {
		gen.let(valid, _`${data} === null`);
		cond = not(valid);
	} else {
		gen.let(valid, false);
	}
	return [valid, cond];
}

export function checkNullableObject(cxt: KeywordCxt, cond: Code): [Name, Code] {
	const [valid, cond_] = checkNullable(cxt, cond);
	return [
		valid,
		_`${cond_} && typeof ${cxt.data} == "object" && !Array.isArray(${cxt.data})`,
	];
}
