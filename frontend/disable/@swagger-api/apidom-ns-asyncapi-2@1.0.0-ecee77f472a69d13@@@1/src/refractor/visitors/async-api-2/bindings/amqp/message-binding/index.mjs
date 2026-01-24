import { always } from "ramda";
import { Mixin } from "ts-mixer";
import AmqpMessageBindingElement from "../../../../../../elements/bindings/amqp/AmqpMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AmqpMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new AmqpMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"amqp",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default AmqpMessageBindingVisitor;
