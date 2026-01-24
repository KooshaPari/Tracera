import HeaderExamplesElement from "../../../../elements/nces/HeaderExamples.mjs";
import BaseExamplesVisitor from "../ExamplesVisitor.mjs";

/**
 * @public
 */
class ExamplesVisitor extends BaseExamplesVisitor {
	constructor(options) {
		super(options);
		this.element = new HeaderExamplesElement();
	}
}
export default ExamplesVisitor;
