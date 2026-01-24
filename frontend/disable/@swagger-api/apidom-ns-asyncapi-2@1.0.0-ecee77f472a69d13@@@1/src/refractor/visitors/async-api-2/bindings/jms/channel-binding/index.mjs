import { always } from "ramda";
import { Mixin } from "ts-mixer";
import JmsChannelBindingElement from "../../../../../../elements/bindings/jms/JmsChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class JmsChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new JmsChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"jms",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default JmsChannelBindingVisitor;
