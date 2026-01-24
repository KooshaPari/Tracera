import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ParametersDefinitionsElement from "../../../../elements/ParametersDefinitions.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ParametersDefinitionsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ParametersDefinitionsElement();
		this.specPath = always(["document", "objects", "Parameter"]);
	}
}
export default ParametersDefinitionsVisitor;
