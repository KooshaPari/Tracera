import { isObjectElement, toValue } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import EncodingElement from "../../../../elements/Encoding.mjs";
import { isHeaderElement } from "../../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class EncodingVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new EncodingElement();
		this.specPath = always(["document", "objects", "Encoding"]);
		this.canSupportSpecificationExtensions = true;
	}
	ObjectElement(objectElement) {
		const result = FixedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// decorate every Header with media type metadata
		if (isObjectElement(this.element.headers)) {
			this.element.headers
				.filter(isHeaderElement)
				// @ts-expect-error
				.forEach((headerElement, key) => {
					headerElement.setMetaProperty("header-name", toValue(key));
				});
		}
		return result;
	}
}
export default EncodingVisitor;
