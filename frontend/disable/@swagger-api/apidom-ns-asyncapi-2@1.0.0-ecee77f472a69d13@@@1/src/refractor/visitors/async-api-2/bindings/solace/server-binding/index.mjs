import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SolaceServerBindingElement from "../../../../../../elements/bindings/solace/SolaceServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SolaceServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SolaceServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"solace",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SolaceServerBindingVisitor;
