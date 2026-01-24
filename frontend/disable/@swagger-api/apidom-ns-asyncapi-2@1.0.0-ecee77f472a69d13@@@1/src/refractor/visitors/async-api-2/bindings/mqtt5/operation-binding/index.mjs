import { always } from "ramda";
import { Mixin } from "ts-mixer";
import Mqtt5OperationBindingElement from "../../../../../../elements/bindings/mqtt5/Mqtt5OperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class Mqtt5OperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new Mqtt5OperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt5",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default Mqtt5OperationBindingVisitor;
