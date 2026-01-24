import { Mixin } from "ts-mixer";
import ResponseLinksElement from "../../../../elements/nces/ResponseLinks.mjs";
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
class LinksVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ResponseLinksElement();
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Link"];
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "link");
		});
		return result;
	}
}
export default LinksVisitor;
