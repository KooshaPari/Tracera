// TODO: add a type for "types" https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/types/js-yaml/index.d.ts
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error

import type { DumpOptions, LoadOptions } from "js-yaml";
import { dump, JSON_SCHEMA, load, types } from "js-yaml";

const DEFAULT_SCHEMA_WITHOUT_TIMESTAMP = JSON_SCHEMA.extend({
	implicit: [types.merge],
	explicit: [types.binary, types.omap, types.pairs, types.set],
});

export const parseYaml = (str: string, opts?: LoadOptions): unknown =>
	load(str, { schema: DEFAULT_SCHEMA_WITHOUT_TIMESTAMP, ...opts });

export const stringifyYaml = (obj: any, opts?: DumpOptions): string =>
	dump(obj, opts);
