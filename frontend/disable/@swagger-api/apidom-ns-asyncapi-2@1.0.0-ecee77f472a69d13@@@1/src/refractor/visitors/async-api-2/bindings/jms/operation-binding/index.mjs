import { always } from "ramda";
import { Mixin } from "ts-mixer";
import JmsOperationBindingElement from "../../../../../../elements/bindings/jms/JmsOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class JmsOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new JmsOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"jms",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default JmsOperationBindingVisitor;
