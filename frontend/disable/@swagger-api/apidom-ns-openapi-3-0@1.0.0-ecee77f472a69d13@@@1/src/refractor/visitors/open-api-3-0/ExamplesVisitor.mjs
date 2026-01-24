import { ObjectElement } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import { isReferenceElement } from "../../../predicates.mjs";
import { isReferenceLikeElement } from "../../predicates.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import MapVisitor from "../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ExamplesVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ObjectElement();
		this.element.classes.push("examples");
		this.specPath = (element) =>
			isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Example"];
		this.canSupportSpecificationExtensions = true;
	}
	ObjectElement(objectElement) {
		const result = MapVisitor.prototype.ObjectElement.call(this, objectElement);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "example");
		});
		return result;
	}
}
export default ExamplesVisitor;
