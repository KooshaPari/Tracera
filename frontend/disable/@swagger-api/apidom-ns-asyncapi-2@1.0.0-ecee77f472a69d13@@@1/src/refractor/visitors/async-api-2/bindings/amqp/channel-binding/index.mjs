import { always } from "ramda";
import { Mixin } from "ts-mixer";
import AmqpChannelBindingElement from "../../../../../../elements/bindings/amqp/AmqpChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AmqpChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new AmqpChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"amqp",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default AmqpChannelBindingVisitor;
