import { always } from "ramda";
import { Mixin } from "ts-mixer";
import PulsarServerBindingElement from "../../../../../../elements/bindings/pulsar/PulsarServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class PulsarServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new PulsarServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"pulsar",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default PulsarServerBindingVisitor;
