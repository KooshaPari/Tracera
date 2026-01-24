import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import OperationSecurityElement from "../../../../elements/nces/OperationSecurity.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SecurityVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new OperationSecurityElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const securityRequirementElement = this.toRefractedElement(
				["document", "objects", "SecurityRequirement"],
				item,
			);
			this.element.push(securityRequirementElement);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default SecurityVisitor;
