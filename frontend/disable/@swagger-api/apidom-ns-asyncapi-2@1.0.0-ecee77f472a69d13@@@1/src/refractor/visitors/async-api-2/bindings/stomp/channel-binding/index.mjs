import { always } from "ramda";
import { Mixin } from "ts-mixer";
import StompChannelBindingElement from "../../../../../../elements/bindings/stomp/StompChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class StompChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new StompChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"stomp",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default StompChannelBindingVisitor;
