import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import StepOnSuccessElement from "../../../../elements/nces/StepOnSuccess.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class OnSuccessVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new StepOnSuccessElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const specPath = ["document", "objects", "SuccessAction"];
			const element = this.toRefractedElement(specPath, item);
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default OnSuccessVisitor;
