import { always } from "ramda";
import { Mixin } from "ts-mixer";
import Amqp1MessageBindingElement from "../../../../../../elements/bindings/amqp1/Amqp1MessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class Amqp1MessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new Amqp1MessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"amqp1",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default Amqp1MessageBindingVisitor;
