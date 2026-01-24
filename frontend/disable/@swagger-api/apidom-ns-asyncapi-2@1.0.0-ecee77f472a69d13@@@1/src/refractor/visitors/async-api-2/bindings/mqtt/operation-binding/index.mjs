import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MqttOperationBindingElement from "../../../../../../elements/bindings/mqtt/MqttOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MqttOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MqttOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MqttOperationBindingVisitor;
