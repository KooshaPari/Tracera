import { always } from "ramda";
import { Mixin } from "ts-mixer";
import Amqp1ChannelBindingElement from "../../../../../../elements/bindings/amqp1/Amqp1ChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class Amqp1ChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new Amqp1ChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"amqp1",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default Amqp1ChannelBindingVisitor;
