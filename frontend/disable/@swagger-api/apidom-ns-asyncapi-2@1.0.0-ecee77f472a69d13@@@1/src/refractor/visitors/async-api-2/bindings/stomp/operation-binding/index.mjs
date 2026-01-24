import { always } from "ramda";
import { Mixin } from "ts-mixer";
import StompOperationBindingElement from "../../../../../../elements/bindings/stomp/StompOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class StompOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new StompOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"stomp",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default StompOperationBindingVisitor;
