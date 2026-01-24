import { BREAK, toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import OpenapiElement from "../../../elements/Openapi.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class OpenapiVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	StringElement(stringElement) {
		const openapiElement = new OpenapiElement(toValue(stringElement));
		this.copyMetaAndAttributes(stringElement, openapiElement);
		this.element = openapiElement;
		return BREAK;
	}
}
export default OpenapiVisitor;
