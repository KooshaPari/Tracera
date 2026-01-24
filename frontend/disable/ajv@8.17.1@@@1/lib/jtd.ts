import type { SchemaEnv } from "./compile";
import compileParser from "./compile/jtd/parse";
import compileSerializer from "./compile/jtd/serialize";
import AjvCore, { type CurrentOptions } from "./core";
import jtdMetaSchema from "./refs/jtd-schema";
import type { AnySchemaObject, JTDParser, SchemaObject } from "./types";
import type {
	JTDDataType,
	JTDSchemaType,
	SomeJTDSchemaType,
} from "./types/jtd-schema";
import jtdVocabulary from "./vocabularies/jtd";

const META_SCHEMA_ID = "JTD-meta-schema";

type JTDOptions = CurrentOptions & {
	// strict mode options not supported with JTD:
	strict?: never;
	allowMatchingProperties?: never;
	allowUnionTypes?: never;
	validateFormats?: never;
	// validation and reporting options not supported with JTD:
	$data?: never;
	verbose?: boolean;
	$comment?: never;
	formats?: never;
	loadSchema?: never;
	// options to modify validated data:
	useDefaults?: never;
	coerceTypes?: never;
	// advanced options:
	next?: never;
	unevaluated?: never;
	dynamicRef?: never;
	meta?: boolean;
	defaultMeta?: never;
	inlineRefs?: boolean;
	loopRequired?: never;
	multipleOfPrecision?: never;
};

export class Ajv extends AjvCore {
	constructor(opts: JTDOptions = {}) {
		super({
			...opts,
			jtd: true,
		});
	}

	_addVocabularies(): void {
		super._addVocabularies();
		this.addVocabulary(jtdVocabulary);
	}

	_addDefaultMetaSchema(): void {
		super._addDefaultMetaSchema();
		if (!this.opts.meta) return;
		this.addMetaSchema(jtdMetaSchema, META_SCHEMA_ID, false);
	}

	defaultMeta(): string | AnySchemaObject | undefined {
		return (this.opts.defaultMeta =
			super.defaultMeta() ||
			(this.getSchema(META_SCHEMA_ID) ? META_SCHEMA_ID : undefined));
	}

	compileSerializer<T = unknown>(schema: SchemaObject): (data: T) => string;
	// Separated for type inference to work
	// eslint-disable-next-line @typescript-eslint/unified-signatures
	compileSerializer<T = unknown>(schema: JTDSchemaType<T>): (data: T) => string;
	compileSerializer<T = unknown>(schema: SchemaObject): (data: T) => string {
		const sch = this._addSchema(schema);
		return sch.serialize || this._compileSerializer(sch);
	}

	compileParser<T = unknown>(schema: SchemaObject): JTDParser<T>;
	// Separated for type inference to work
	// eslint-disable-next-line @typescript-eslint/unified-signatures
	compileParser<T = unknown>(schema: JTDSchemaType<T>): JTDParser<T>;
	compileParser<T = unknown>(schema: SchemaObject): JTDParser<T> {
		const sch = this._addSchema(schema);
		return (sch.parse || this._compileParser(sch)) as JTDParser<T>;
	}

	private _compileSerializer<T>(sch: SchemaEnv): (data: T) => string {
		compileSerializer.call(
			this,
			sch,
			(sch.schema as AnySchemaObject).definitions || {},
		);
		/* istanbul ignore if */
		if (!sch.serialize) throw new Error("ajv implementation error");
		return sch.serialize;
	}

	private _compileParser(sch: SchemaEnv): JTDParser {
		compileParser.call(
			this,
			sch,
			(sch.schema as AnySchemaObject).definitions || {},
		);
		/* istanbul ignore if */
		if (!sch.parse) throw new Error("ajv implementation error");
		return sch.parse;
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
export { KeywordCxt } from "./compile/validate";
export {
	CodeOptions,
	ErrorsTextOptions,
	InstanceOptions,
	Logger,
	Options,
	Plugin,
} from "./core";
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
	JTDParser,
	KeywordDefinition,
	KeywordErrorDefinition,
	MacroKeywordDefinition,
	Schema,
	SchemaObject,
	ValidateFunction,
	Vocabulary,
} from "./types";
export { JTDErrorObject } from "./vocabularies/jtd";

export type { JTDSchemaType, SomeJTDSchemaType, JTDDataType };
export type { JTDOptions };
export { default as MissingRefError } from "./compile/ref_error";
export { default as ValidationError } from "./runtime/validation_error";
