import { always } from "ramda";
import { Mixin } from "ts-mixer";
import NatsOperationBindingElement from "../../../../../../elements/bindings/nats/NatsOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class NatsOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new NatsOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"nats",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default NatsOperationBindingVisitor;
