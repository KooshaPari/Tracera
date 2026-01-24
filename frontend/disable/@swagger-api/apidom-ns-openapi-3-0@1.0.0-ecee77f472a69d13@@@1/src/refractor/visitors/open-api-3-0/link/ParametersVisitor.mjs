import { always } from "ramda";
import { Mixin } from "ts-mixer";
import LinkParametersElement from "../../../../elements/nces/LinkParameters.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ParametersVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new LinkParametersElement();
		this.specPath = always(["value"]);
	}
}
export default ParametersVisitor;
