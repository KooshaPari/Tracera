import { isStringElement } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import LinkElement from "../../../../elements/Link.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class LinkVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new LinkElement();
		this.specPath = always(["document", "objects", "Link"]);
		this.canSupportSpecificationExtensions = true;
	}
	ObjectElement(objectElement) {
		const result = FixedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// mark this LinkElement with reference metadata
		if (
			isStringElement(this.element.operationId) ||
			isStringElement(this.element.operationRef)
		) {
			this.element.classes.push("reference-element");
		}
		return result;
	}
}
export default LinkVisitor;
