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

export type { infer, input, output } from "../core/index.js";
export {
	$brand,
	$input,
	$output,
	clone,
	config,
	flattenError,
	formatError,
	function,
	type GlobalMeta,
	globalRegistry,
	NEVER,
	prettifyError,
	regexes,
	registry,
	TimePrecision,
	toJSONSchema,
	treeifyError,
} from "../core/index.js";

export * as locales from "../locales/index.js";
// coerce
export type {
	ZodCoercedBigInt,
	ZodCoercedBoolean,
	ZodCoercedDate,
	ZodCoercedNumber,
	ZodCoercedString,
} from "./coerce.js";
export * as coerce from "./coerce.js";
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
