import { always } from "ramda";
import { Mixin } from "ts-mixer";
import PulsarChannelBindingElement from "../../../../../../elements/bindings/pulsar/PulsarChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class PulsarChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new PulsarChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"pulsar",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default PulsarChannelBindingVisitor;
