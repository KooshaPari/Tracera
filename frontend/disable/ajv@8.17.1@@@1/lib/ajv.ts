import AjvCore from "./core";
import * as draft7MetaSchema from "./refs/json-schema-draft-07.json";
import type { AnySchemaObject } from "./types";
import discriminator from "./vocabularies/discriminator";
import draft7Vocabularies from "./vocabularies/draft7";

const META_SUPPORT_DATA = ["/properties"];

const META_SCHEMA_ID = "http://json-schema.org/draft-07/schema";

export class Ajv extends AjvCore {
	_addVocabularies(): void {
		super._addVocabularies();
		draft7Vocabularies.forEach((v) => this.addVocabulary(v));
		if (this.opts.discriminator) this.addKeyword(discriminator);
	}

	_addDefaultMetaSchema(): void {
		super._addDefaultMetaSchema();
		if (!this.opts.meta) return;
		const metaSchema = this.opts.$data
			? this.$dataMetaSchema(draft7MetaSchema, META_SUPPORT_DATA)
			: draft7MetaSchema;
		this.addMetaSchema(metaSchema, META_SCHEMA_ID, false);
		this.refs["http://json-schema.org/schema"] = META_SCHEMA_ID;
	}

	defaultMeta(): string | AnySchemaObject | undefined {
		return (this.opts.defaultMeta =
			super.defaultMeta() ||
			(this.getSchema(META_SCHEMA_ID) ? META_SCHEMA_ID : undefined));
	}
}

module.exports = exports = Ajv;
module.exports.Ajv = Ajv;
Object.defineProperty(exports, "__esModule", { value: true });

export default Ajv;

export { SchemaCxt, SchemaObjCxt } from "./compile";
export {
	_,
	Code,
	CodeGen,
	CodeGenOptions,
	Name,
	nil,
	str,
	stringify,
} from "./compile/codegen";
export { default as MissingRefError } from "./compile/ref_error";
export { JSONType } from "./compile/rules";
export { KeywordCxt } from "./compile/validate";
export {
	CodeOptions,
	ErrorsTextOptions,
	InstanceOptions,
	Logger,
	Options,
	Plugin,
} from "./core";
export { default as ValidationError } from "./runtime/validation_error";
export {
	AnySchema,
	AnySchemaObject,
	AsyncFormatDefinition,
	AsyncSchema,
	AsyncValidateFunction,
	CodeKeywordDefinition,
	ErrorNoParams,
	ErrorObject,
	Format,
	FormatDefinition,
	FuncKeywordDefinition,
	KeywordDefinition,
	KeywordErrorDefinition,
	MacroKeywordDefinition,
	Schema,
	SchemaObject,
	SchemaValidateFunction,
	ValidateFunction,
	Vocabulary,
} from "./types";
export { JSONSchemaType } from "./types/json-schema";
export { DefinedError } from "./vocabularies/errors";
