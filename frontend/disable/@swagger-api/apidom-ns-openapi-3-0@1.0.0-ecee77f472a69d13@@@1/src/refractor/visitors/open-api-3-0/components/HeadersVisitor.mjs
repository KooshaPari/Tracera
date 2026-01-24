import { toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import ComponentsHeadersElement from "../../../../elements/nces/ComponentsHeaders.mjs";
import {
	isHeaderElement,
	isReferenceElement,
} from "../../../../predicates.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class HeadersVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsHeadersElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Header"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// decorate every ReferenceElement with metadata about their referencing type
		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "header");
		});

		// decorate every HeaderElement with metadata about their name
		// @ts-expect-error
		this.element.filter(isHeaderElement).forEach((value, key) => {
			value.setMetaProperty("header-name", toValue(key));
		});
		return result;
	}
}
export default HeadersVisitor;
