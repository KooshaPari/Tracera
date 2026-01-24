import { Mixin } from "ts-mixer";
import ParametersElement from "../../../../elements/Parameters.mjs";
import { isReferenceElement } from "../../../../predicates.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import PatternedFieldsVisitor from "../../generics/PatternedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ParametersVisitor extends Mixin(PatternedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ParametersElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Parameter"];
		this.canSupportSpecificationExtensions = false;
		this.fieldPatternPredicate = (value) =>
			typeof value === "string" && /^[A-Za-z0-9_-]+$/.test(value);
	}
	ObjectElement(objectElement) {
		const result = PatternedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "parameter");
		});
		return result;
	}
}
export default ParametersVisitor;
