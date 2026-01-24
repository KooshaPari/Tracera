import { BREAK, cloneDeep, isObjectElement } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import SecurityElement from "../../../elements/nces/Security.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SecurityVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new SecurityElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			if (isObjectElement(item)) {
				const element = this.toRefractedElement(
					["document", "objects", "SecurityRequirement"],
					item,
				);
				this.element.push(element);
			} else {
				this.element.push(cloneDeep(item));
			}
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default SecurityVisitor;
