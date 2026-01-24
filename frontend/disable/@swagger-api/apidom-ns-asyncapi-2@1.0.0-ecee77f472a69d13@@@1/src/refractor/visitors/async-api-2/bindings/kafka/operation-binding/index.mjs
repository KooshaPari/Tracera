import { always } from "ramda";
import { Mixin } from "ts-mixer";
import KafkaOperationBindingElement from "../../../../../../elements/bindings/kafka/KafkaOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class KafkaOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new KafkaOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"kafka",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default KafkaOperationBindingVisitor;
