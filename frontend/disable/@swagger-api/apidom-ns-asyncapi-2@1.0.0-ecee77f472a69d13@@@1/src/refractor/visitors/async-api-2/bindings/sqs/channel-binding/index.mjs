import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SqsChannelBindingElement from "../../../../../../elements/bindings/sqs/SqsChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SqsChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SqsChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"sqs",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SqsChannelBindingVisitor;
