import { always } from "ramda";
import { Mixin } from "ts-mixer";
import KafkaMessageBindingElement from "../../../../../../elements/bindings/kafka/KafkaMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class KafkaMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new KafkaMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"kafka",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default KafkaMessageBindingVisitor;
