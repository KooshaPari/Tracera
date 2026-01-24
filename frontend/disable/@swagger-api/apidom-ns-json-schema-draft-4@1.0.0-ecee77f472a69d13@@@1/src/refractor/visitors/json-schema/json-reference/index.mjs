import { isStringElement } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import JSONReferenceElement from "../../../../elements/JSONReference.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class JSONReferenceVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new JSONReferenceElement();
		this.specPath = always(["document", "objects", "JSONReference"]);
	}
	ObjectElement(objectElement) {
		const result = FixedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// mark this JSONReferenceElement with reference metadata
		if (isStringElement(this.element.$ref)) {
			this.element.classes.push("reference-element");
		}
		return result;
	}
}
export default JSONReferenceVisitor;
