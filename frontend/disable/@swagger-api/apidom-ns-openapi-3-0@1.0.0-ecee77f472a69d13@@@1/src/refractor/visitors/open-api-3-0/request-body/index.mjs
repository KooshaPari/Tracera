import { isObjectElement, toValue } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import RequestBodyElement from "../../../../elements/RequestBody.mjs";
import { isMediaTypeElement } from "../../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class RequestBodyVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new RequestBodyElement();
		this.specPath = always(["document", "objects", "RequestBody"]);
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
export default RequestBodyVisitor;
