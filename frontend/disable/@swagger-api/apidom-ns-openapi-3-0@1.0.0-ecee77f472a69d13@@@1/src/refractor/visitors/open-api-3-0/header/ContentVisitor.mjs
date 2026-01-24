import HeaderContentElement from "../../../../elements/nces/HeaderContent.mjs";
import BaseContentVisitor from "../ContentVisitor.mjs";

/**
 * @public
 */
class ContentVisitor extends BaseContentVisitor {
	constructor(options) {
		super(options);
		this.element = new HeaderContentElement();
	}
}
export default ContentVisitor;
