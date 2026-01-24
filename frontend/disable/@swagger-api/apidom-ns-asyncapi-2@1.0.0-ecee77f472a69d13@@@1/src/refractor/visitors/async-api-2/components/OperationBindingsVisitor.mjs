import { Mixin } from "ts-mixer";
import ComponentsOperationBindingsElement from "../../../../elements/nces/ComponentsOperationBindings.mjs";
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
class OperationBindingsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsOperationBindingsElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "OperationBindings"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty(
				"referenced-element",
				"operationBindings",
			);
		});
		return result;
	}
}
export default OperationBindingsVisitor;
