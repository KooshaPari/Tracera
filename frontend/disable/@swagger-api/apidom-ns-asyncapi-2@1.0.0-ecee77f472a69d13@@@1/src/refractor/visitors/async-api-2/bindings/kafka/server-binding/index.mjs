import { always } from "ramda";
import { Mixin } from "ts-mixer";
import KafkaServerBindingElement from "../../../../../../elements/bindings/kafka/KafkaServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class KafkaServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new KafkaServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"kafka",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default KafkaServerBindingVisitor;
