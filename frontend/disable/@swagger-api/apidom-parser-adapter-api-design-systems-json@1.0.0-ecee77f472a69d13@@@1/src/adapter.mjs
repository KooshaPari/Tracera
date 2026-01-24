import { createNamespace } from "@swagger-api/apidom-core";
import apiDesignSystemsNamespace, {
	MainElement,
} from "@swagger-api/apidom-ns-api-design-systems";
import {
	detect as detectJSON,
	parse as parseJSON,
} from "@swagger-api/apidom-parser-adapter-json";
import { omit, propOr } from "ramda";
import { isNotUndefined } from "ramda-adjunct";

export { default as mediaTypes } from "./media-types.mjs";
/**
 * @public
 */
export const detectionRegExp = /"version"\s*:\s*"(?<version_json>2021-05-07)"/;

/**
 * @public
 */
export const detect = async (source) =>
	detectionRegExp.test(source) && (await detectJSON(source));

/**
 * @public
 */
export const parse = async (source, options = {}) => {
	const refractorOpts = propOr({}, "refractorOpts", options);
	const parserOpts = omit(["refractorOpts"], options);
	const parseResultElement = await parseJSON(source, parserOpts);
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
