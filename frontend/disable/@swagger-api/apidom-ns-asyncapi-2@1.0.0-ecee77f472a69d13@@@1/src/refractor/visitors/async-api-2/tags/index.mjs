import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import TagsElement from "../../../../elements/Tags.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

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
			const tagElement = this.toRefractedElement(
				["document", "objects", "Tag"],
				item,
			);
			this.element.push(tagElement);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default TagsVisitor;
