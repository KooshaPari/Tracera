import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import MessageExamplesElement from "../../../../elements/nces/MessageExamples.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ExamplesVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new MessageExamplesElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const messageElement = this.toRefractedElement(
				["document", "objects", "MessageExample"],
				item,
			);
			this.element.push(messageElement);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default ExamplesVisitor;
