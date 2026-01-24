import { always } from "ramda";
import { Mixin } from "ts-mixer";
import PulsarOperationBindingElement from "../../../../../../elements/bindings/pulsar/PulsarOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class PulsarOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new PulsarOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"pulsar",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default PulsarOperationBindingVisitor;
