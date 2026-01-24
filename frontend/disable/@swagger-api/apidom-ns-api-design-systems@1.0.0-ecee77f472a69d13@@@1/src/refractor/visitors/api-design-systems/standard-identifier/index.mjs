import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import StandardIdentifierElement from "../../../../elements/StandardIdentifier.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class StandardIdentifierVisitor extends Mixin(
	SpecificationVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new StandardIdentifierElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const specPath = ["document", "objects", "StandardIdentifier"];
			const element = this.toRefractedElement(specPath, item);
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default StandardIdentifierVisitor;
