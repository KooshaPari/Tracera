import ParameterContentElement from "../../../../elements/nces/ParameterContent.mjs";
import BaseContentVisitor from "../ContentVisitor.mjs";

/**
 * @public
 */
class ContentVisitor extends BaseContentVisitor {
	constructor(options) {
		super(options);
		this.element = new ParameterContentElement();
	}
}
export default ContentVisitor;
