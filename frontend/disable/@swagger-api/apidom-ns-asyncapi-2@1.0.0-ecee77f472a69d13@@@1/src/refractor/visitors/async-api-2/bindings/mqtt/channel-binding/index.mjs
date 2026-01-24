import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MqttChannelBindingElement from "../../../../../../elements/bindings/mqtt/MqttChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MqttChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MqttChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MqttChannelBindingVisitor;
