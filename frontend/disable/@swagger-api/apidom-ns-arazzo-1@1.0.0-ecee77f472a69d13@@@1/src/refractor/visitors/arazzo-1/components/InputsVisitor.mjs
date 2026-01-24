import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ComponentsInputsElement from "../../../../elements/nces/ComponentsInputs.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class InputsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsInputsElement();
		this.specPath = always(["document", "objects", "JSONSchema"]);
	}
}
export default InputsVisitor;
