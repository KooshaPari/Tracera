import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SolaceChannelBindingElement from "../../../../../../elements/bindings/solace/SolaceChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SolaceChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SolaceChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"solace",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SolaceChannelBindingVisitor;
