import AjvCore, { type Options } from "./core";
import addMetaSchema2020 from "./refs/json-schema-2020-12";
import type { AnySchemaObject } from "./types";
import discriminator from "./vocabularies/discriminator";
import draft2020Vocabularies from "./vocabularies/draft2020";

const META_SCHEMA_ID = "https://json-schema.org/draft/2020-12/schema";

export class Ajv2020 extends AjvCore {
	constructor(opts: Options = {}) {
		super({
			...opts,
			dynamicRef: true,
			next: true,
			unevaluated: true,
		});
	}

	_addVocabularies(): void {
		super._addVocabularies();
		draft2020Vocabularies.forEach((v) => this.addVocabulary(v));
		if (this.opts.discriminator) this.addKeyword(discriminator);
	}

	_addDefaultMetaSchema(): void {
		super._addDefaultMetaSchema();
		const { $data, meta } = this.opts;
		if (!meta) return;
		addMetaSchema2020.call(this, $data);
		this.refs["http://json-schema.org/schema"] = META_SCHEMA_ID;
	}

	defaultMeta(): string | AnySchemaObject | undefined {
		return (this.opts.defaultMeta =
			super.defaultMeta() ||
			(this.getSchema(META_SCHEMA_ID) ? META_SCHEMA_ID : undefined));
	}
}

module.exports = exports = Ajv2020;
module.exports.Ajv2020 = Ajv2020;
Object.defineProperty(exports, "__esModule", { value: true });

export default Ajv2020;

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
	ValidateFunction,
	Vocabulary,
} from "./types";
export { JSONSchemaType } from "./types/json-schema";
export { DefinedError } from "./vocabularies/errors";
