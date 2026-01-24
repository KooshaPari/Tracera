import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MqttServerBindingElement from "../../../../../../elements/bindings/mqtt/MqttServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MqttServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MqttServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MqttServerBindingVisitor;
