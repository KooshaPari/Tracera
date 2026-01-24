import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import WorkflowStepsElement from "../../../../elements/nces/WorkflowSteps.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class StepsVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new WorkflowStepsElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const specPath = ["document", "objects", "Step"];
			const element = this.toRefractedElement(specPath, item);
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default StepsVisitor;
