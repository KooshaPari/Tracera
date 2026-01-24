import { always } from "ramda";
import { Mixin } from "ts-mixer";
import WorkflowOutputsElement from "../../../../elements/nces/WorkflowOutputs.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class OutputsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new WorkflowOutputsElement();
		this.specPath = always(["value"]);
	}
}
export default OutputsVisitor;
