import { always } from "ramda";
import { Mixin } from "ts-mixer";
import KafkaChannelBindingElement from "../../../../../../elements/bindings/kafka/KafkaChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class KafkaChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new KafkaChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"kafka",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default KafkaChannelBindingVisitor;
