import { Mixin } from "ts-mixer";
import ComponentsRequestBodiesElement from "../../../../elements/nces/ComponentsRequestBodies.mjs";
import { isReferenceElement } from "../../../../predicates.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class RequestBodiesVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsRequestBodiesElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "RequestBody"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "requestBody");
		});
		return result;
	}
}
export default RequestBodiesVisitor;
