/**
 * Created by kor on 06/05/15.
 */

export { dump, safeDump } from "./dumper";
export { LoadOptions, load, loadAll, safeLoad, safeLoadAll } from "./loader";

import Mark = require("./mark");
export import YAMLException = require("./exception");

export * from "./yamlAST";

export type Error = YAMLException;

function deprecated(name) {
	return () => {
		throw new Error("Function " + name + " is deprecated and cannot be used.");
	};
}

export * from "./scalarInference";
