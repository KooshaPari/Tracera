export * as core from "../core/index.js";
export * from "./checks.js";
export * from "./compat.js";
export * from "./errors.js";
export * from "./parse.js";
export * from "./schemas.js";

// zod-specified
import { config } from "../core/index.js";
import en from "../locales/en.js";

config(en());

export {
	$brand,
	$input,
	$output,
	clone,
	config,
	flattenError,
	formatError,
	globalRegistry,
	NEVER,
	prettifyError,
	regexes,
	registry,
	TimePrecision,
	treeifyError,
	util,
} from "../core/index.js";
export { toJSONSchema } from "../core/json-schema-processors.js";
export * as locales from "../locales/index.js";
export * as coerce from "./coerce.js";
export { fromJSONSchema } from "./from-json-schema.js";
export * as iso from "./iso.js";
// iso
// must be exported from top-level
// https://github.com/colinhacks/zod/issues/4491
export {
	ZodISODate,
	ZodISODateTime,
	ZodISODuration,
	ZodISOTime,
} from "./iso.js";
