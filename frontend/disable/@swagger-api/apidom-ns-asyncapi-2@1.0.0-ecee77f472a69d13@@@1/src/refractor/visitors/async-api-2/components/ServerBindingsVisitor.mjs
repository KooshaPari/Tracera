import { Mixin } from "ts-mixer";
import ComponentsServerBindingsElement from "../../../../elements/nces/ComponentsServerBindings.mjs";
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
class ServerBindingsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsServerBindingsElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "ServerBindings"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "serverBindings");
		});
		return result;
	}
}
export default ServerBindingsVisitor;
