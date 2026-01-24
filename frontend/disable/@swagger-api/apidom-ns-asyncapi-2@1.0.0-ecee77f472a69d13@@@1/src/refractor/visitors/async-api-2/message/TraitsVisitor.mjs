import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import MessageTraitsElement from "../../../../elements/nces/MessageTraits.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class TraitsVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new MessageTraitsElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			let element;
			if (isReferenceLikeElement(item)) {
				element = this.toRefractedElement(
					["document", "objects", "Reference"],
					item,
				);
				element.setMetaProperty("referenced-element", "messageTrait");
			} else {
				element = this.toRefractedElement(
					["document", "objects", "MessageTrait"],
					item,
				);
			}
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default TraitsVisitor;
