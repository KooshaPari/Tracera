import { BREAK, toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import AsyncApiVersionElement from "../../../elements/AsyncApiVersion.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AsyncApiVersionVisitor extends Mixin(
	SpecificationVisitor,
	FallbackVisitor,
) {
	StringElement(stringElement) {
		const asyncApiVersionElement = new AsyncApiVersionElement(
			toValue(stringElement),
		);
		this.copyMetaAndAttributes(stringElement, asyncApiVersionElement);
		this.element = asyncApiVersionElement;
		return BREAK;
	}
}
export default AsyncApiVersionVisitor;
