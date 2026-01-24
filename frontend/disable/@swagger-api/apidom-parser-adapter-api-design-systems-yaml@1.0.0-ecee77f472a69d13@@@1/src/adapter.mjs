import { createNamespace } from "@swagger-api/apidom-core";
import apiDesignSystemsNamespace, {
	MainElement,
} from "@swagger-api/apidom-ns-api-design-systems";
import {
	detect as detectYAML,
	parse as parseYAML,
} from "@swagger-api/apidom-parser-adapter-yaml-1-2";
import { omit, propOr } from "ramda";
import { isNotUndefined } from "ramda-adjunct";

export { default as mediaTypes } from "./media-types.mjs";
/**
 * @public
 */
export const detectionRegExp =
	/(?<YAML>^(["']?)version\2\s*:\s*(["']?)(?<version_yaml>2021-05-07)\3)|(?<JSON>"version"\s*:\s*"(?<version_json>2021-05-07)")/m;

/**
 * @public
 */
export const detect = async (source) =>
	detectionRegExp.test(source) && (await detectYAML(source));

/**
 * @public
 */
export const parse = async (source, options = {}) => {
	const refractorOpts = propOr({}, "refractorOpts", options);
	const parserOpts = omit(["refractorOpts"], options);
	const parseResultElement = await parseYAML(source, parserOpts);
	const { result } = parseResultElement;
	if (isNotUndefined(result)) {
		const mainElement = MainElement.refract(result, refractorOpts);
		mainElement.classes.push("result");
		parseResultElement.replaceResult(mainElement);
	}
	return parseResultElement;
};

/**
 * @public
 */
export const namespace = createNamespace(apiDesignSystemsNamespace);
