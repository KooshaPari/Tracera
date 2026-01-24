import { always } from "ramda";
import { Mixin } from "ts-mixer";
import NatsMessageBindingElement from "../../../../../../elements/bindings/nats/NatsMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class NatsMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new NatsMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"nats",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default NatsMessageBindingVisitor;
