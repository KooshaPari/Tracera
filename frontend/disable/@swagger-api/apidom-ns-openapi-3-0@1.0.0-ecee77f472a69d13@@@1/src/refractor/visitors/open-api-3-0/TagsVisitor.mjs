import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import TagsElement from "../../../elements/nces/Tags.mjs";
import { isTagLikeElement } from "../../predicates.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class TagsVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new TagsElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const specPath = isTagLikeElement(item)
				? ["document", "objects", "Tag"]
				: ["value"];
			const element = this.toRefractedElement(specPath, item);
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default TagsVisitor;
