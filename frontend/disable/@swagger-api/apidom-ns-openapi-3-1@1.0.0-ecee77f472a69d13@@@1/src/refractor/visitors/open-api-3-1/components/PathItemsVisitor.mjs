import {
	FallbackVisitor,
	isReferenceLikeElement,
	MapVisitor,
} from "@swagger-api/apidom-ns-openapi-3-0";
import { Mixin } from "ts-mixer";
import ComponentsPathItemsElement from "../../../../elements/nces/ComponentsPathItems.mjs";
import { isReferenceElement } from "../../../../predicates.mjs";

/**
 * @public
 */
/**
 * @public
 */
class PathItemsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsPathItemsElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "PathItem"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			// @ts-expect-error
			referenceElement.setMetaProperty("referenced-element", "pathItem");
		});
		return result;
	}
}
export default PathItemsVisitor;
