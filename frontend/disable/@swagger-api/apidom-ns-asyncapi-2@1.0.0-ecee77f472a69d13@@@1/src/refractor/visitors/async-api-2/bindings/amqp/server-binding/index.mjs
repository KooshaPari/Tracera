import { always } from "ramda";
import { Mixin } from "ts-mixer";
import AmqpServerBindingElement from "../../../../../../elements/bindings/amqp/AmqpServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AmqpServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new AmqpServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"amqp",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default AmqpServerBindingVisitor;
