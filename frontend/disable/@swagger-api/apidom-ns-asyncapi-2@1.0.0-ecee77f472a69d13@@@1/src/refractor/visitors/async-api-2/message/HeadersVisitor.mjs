import { T as stubTrue } from "ramda";
import { Mixin } from "ts-mixer";
import { isReferenceElement } from "../../../../predicates.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import AlternatingVisitor from "../../generics/AlternatingVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class HeadersVisitor extends Mixin(AlternatingVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.alternator = [
			{
				predicate: isReferenceLikeElement,
				specPath: ["document", "objects", "Reference"],
			},
			{
				predicate: stubTrue,
				specPath: ["document", "objects", "Schema"],
			},
		];
	}
	ObjectElement(objectElement) {
		const result = AlternatingVisitor.prototype.enter.call(this, objectElement);
		if (isReferenceElement(this.element)) {
			this.element.setMetaProperty("referenced-element", "schema");
		}
		return result;
	}
}
export default HeadersVisitor;
