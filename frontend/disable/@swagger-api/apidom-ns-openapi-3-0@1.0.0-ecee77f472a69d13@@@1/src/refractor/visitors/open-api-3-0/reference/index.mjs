import { isStringElement } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ReferenceElement from "../../../../elements/Reference.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ReferenceVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ReferenceElement();
		this.specPath = always(["document", "objects", "Reference"]);
		this.canSupportSpecificationExtensions = false;
	}
	ObjectElement(objectElement) {
		const result = FixedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// mark this ReferenceElement with reference metadata
		if (isStringElement(this.element.$ref)) {
			this.element.classes.push("reference-element");
		}
		return result;
	}
}
export default ReferenceVisitor;
