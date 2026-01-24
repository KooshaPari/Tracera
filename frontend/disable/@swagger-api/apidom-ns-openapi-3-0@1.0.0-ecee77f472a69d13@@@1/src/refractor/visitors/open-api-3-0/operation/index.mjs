import { always } from "ramda";
import { Mixin } from "ts-mixer";
import OperationElement from "../../../../elements/Operation.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class OperationVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new OperationElement();
		this.specPath = always(["document", "objects", "Operation"]);
	}
}
export default OperationVisitor;
