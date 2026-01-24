import { Mixin } from "ts-mixer";
import OperationCallbacksElement from "../../../../elements/nces/OperationCallbacks.mjs";
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
class CallbacksVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	specPath;
	constructor(options) {
		super(options);
		this.element = new OperationCallbacksElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Callback"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "callback");
		});
		return result;
	}
}
export default CallbacksVisitor;
