import { compileSchema, SchemaEnv } from "../../compile";
import { _, type Code, getProperty } from "../../compile/codegen";
import N from "../../compile/names";
import type { KeywordCxt } from "../../compile/validate";
import type { CodeKeywordDefinition } from "../../types";
import { getValidate } from "../core/ref";

const def: CodeKeywordDefinition = {
	keyword: "$dynamicAnchor",
	schemaType: "string",
	code: (cxt) => dynamicAnchor(cxt, cxt.schema),
};

export function dynamicAnchor(cxt: KeywordCxt, anchor: string): void {
	const { gen, it } = cxt;
	it.schemaEnv.root.dynamicAnchors[anchor] = true;
	const v = _`${N.dynamicAnchors}${getProperty(anchor)}`;
	const validate =
		it.errSchemaPath === "#" ? it.validateName : _getValidate(cxt);
	gen.if(_`!${v}`, () => gen.assign(v, validate));
}

function _getValidate(cxt: KeywordCxt): Code {
	const { schemaEnv, schema, self } = cxt.it;
	const { root, baseId, localRefs, meta } = schemaEnv.root;
	const { schemaId } = self.opts;
	const sch = new SchemaEnv({
		schema,
		schemaId,
		root,
		baseId,
		localRefs,
		meta,
	});
	compileSchema.call(self, sch);
	return getValidate(cxt, sch);
}

export default def;
