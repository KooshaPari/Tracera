import { always } from "ramda";
import { Mixin } from "ts-mixer";
import NatsChannelBindingElement from "../../../../../../elements/bindings/nats/NatsChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class NatsChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new NatsChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"nats",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default NatsChannelBindingVisitor;
