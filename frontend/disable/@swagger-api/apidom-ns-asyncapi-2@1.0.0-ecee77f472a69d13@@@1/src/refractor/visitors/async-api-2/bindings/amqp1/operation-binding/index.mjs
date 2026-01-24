import { always } from "ramda";
import { Mixin } from "ts-mixer";
import Amqp1OperationBindingElement from "../../../../../../elements/bindings/amqp1/Amqp1OperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class Amqp1OperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new Amqp1OperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"amqp1",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default Amqp1OperationBindingVisitor;
