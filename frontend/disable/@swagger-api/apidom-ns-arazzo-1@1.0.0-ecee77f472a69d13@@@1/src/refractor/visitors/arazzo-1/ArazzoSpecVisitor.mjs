import { BREAK, toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import ArazzoSpecElement from "../../../elements/ArazzoSpec.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ArazzoSpecVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	StringElement(stringElement) {
		const arazzoSpecElement = new ArazzoSpecElement(toValue(stringElement));
		this.copyMetaAndAttributes(stringElement, arazzoSpecElement);
		this.element = arazzoSpecElement;
		return BREAK;
	}
}
export default ArazzoSpecVisitor;
