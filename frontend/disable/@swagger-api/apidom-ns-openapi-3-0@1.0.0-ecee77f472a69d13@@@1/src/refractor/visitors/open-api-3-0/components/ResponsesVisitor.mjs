import { toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import ComponentsResponsesElement from "../../../../elements/nces/ComponentsResponses.mjs";
import {
	isReferenceElement,
	isResponseElement,
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
class ResponsesVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsResponsesElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Response"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// decorate every ReferenceElement with metadata about their referencing type
		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "response");
		});

		// decorate every ResponseElement with metadata about their status code
		// @ts-expect-error
		this.element.filter(isResponseElement).forEach((value, key) => {
			value.setMetaProperty("http-status-code", toValue(key));
		});
		return result;
	}
}
export default ResponsesVisitor;
