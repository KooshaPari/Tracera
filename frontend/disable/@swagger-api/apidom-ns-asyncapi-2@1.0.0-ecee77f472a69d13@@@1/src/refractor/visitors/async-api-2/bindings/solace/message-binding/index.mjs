import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SolaceMessageBindingElement from "../../../../../../elements/bindings/solace/SolaceMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SolaceMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SolaceMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"solace",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SolaceMessageBindingVisitor;
