import JsonNode from "./JsonNode.mjs";
import {
	isArray,
	isFalse,
	isNull,
	isNumber,
	isObject,
	isString,
	isTrue,
} from "./predicates.mjs";

/**
 * @public
 */
class JsonArray extends JsonNode {
	static type = "array";
	get items() {
		return this.children.filter(
			(node) =>
				isFalse(node) ||
				isTrue(node) ||
				isNull(node) ||
				isNumber(node) ||
				isString(node) ||
				isArray(node) ||
				isObject,
		);
	}
}
export default JsonArray;
