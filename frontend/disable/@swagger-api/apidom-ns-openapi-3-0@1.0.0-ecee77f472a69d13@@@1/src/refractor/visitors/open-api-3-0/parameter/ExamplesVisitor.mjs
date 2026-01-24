import ParameterExamplesElement from "../../../../elements/nces/ParameterExamples.mjs";
import BaseExamplesVisitor from "../ExamplesVisitor.mjs";

/**
 * @public
 */
class ExamplesVisitor extends BaseExamplesVisitor {
	constructor(options) {
		super(options);
		this.element = new ParameterExamplesElement();
	}
}
export default ExamplesVisitor;
