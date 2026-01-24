import { always } from "ramda";
import { Mixin } from "ts-mixer";
import Mqtt5ChannelBindingElement from "../../../../../../elements/bindings/mqtt5/Mqtt5ChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class Mqtt5ChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new Mqtt5ChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt5",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default Mqtt5ChannelBindingVisitor;
