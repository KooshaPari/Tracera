import { always } from "ramda";
import { Mixin } from "ts-mixer";
import CorrelationIDElement from "../../../../elements/CorrelationID.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class CorrelationIDVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new CorrelationIDElement();
		this.specPath = always(["document", "objects", "CorrelationID"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default CorrelationIDVisitor;
