import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MqttMessageBindingElement from "../../../../../../elements/bindings/mqtt/MqttMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MqttMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MqttMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MqttMessageBindingVisitor;
