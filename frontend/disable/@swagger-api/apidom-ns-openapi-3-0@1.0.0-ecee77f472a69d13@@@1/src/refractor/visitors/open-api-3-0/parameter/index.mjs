import { isObjectElement, toValue } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ParameterElement from "../../../../elements/Parameter.mjs";
import { isMediaTypeElement } from "../../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ParameterVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ParameterElement();
		this.specPath = always(["document", "objects", "Parameter"]);
		this.canSupportSpecificationExtensions = true;
	}
	ObjectElement(objectElement) {
		const result = FixedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// decorate every MediaTypeElement with media type metadata
		if (isObjectElement(this.element.contentProp)) {
			this.element.contentProp
				.filter(isMediaTypeElement)
				// @ts-expect-error
				.forEach((mediaTypeElement, key) => {
					mediaTypeElement.setMetaProperty("media-type", toValue(key));
				});
		}
		return result;
	}
}
export default ParameterVisitor;
