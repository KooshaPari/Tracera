import { test } from "ramda";
import { Mixin } from "ts-mixer";
import ServersElement from "../../../../elements/Servers.mjs";
import { isReferenceElement } from "../../../../predicates.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import PatternedFieldsVisitor from "../../generics/PatternedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ServersVisitor extends Mixin(PatternedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ServersElement();
		this.element.classes.push("servers");
		this.specPath = (element) => {
			return isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Server"];
		};
		this.canSupportSpecificationExtensions = false;
		// @ts-expect-error
		this.fieldPatternPredicate = test(/^[A-Za-z0-9_-]+$/);
	}
	ObjectElement(objectElement) {
		const result = PatternedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "server");
		});
		return result;
	}
}
export default ServersVisitor;
