import MediaTypeExamples from "../../../../elements/nces/MediaTypeExamples.mjs";
import BaseExamplesVisitor from "../ExamplesVisitor.mjs";

/**
 * @public
 */
class ExamplesVisitor extends BaseExamplesVisitor {
	constructor(options) {
		super(options);
		this.element = new MediaTypeExamples();
	}
}
export default ExamplesVisitor;
