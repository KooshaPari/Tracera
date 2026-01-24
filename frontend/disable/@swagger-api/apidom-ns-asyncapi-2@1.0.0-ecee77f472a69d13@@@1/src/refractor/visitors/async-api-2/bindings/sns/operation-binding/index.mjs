import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SnsOperationBindingElement from "../../../../../../elements/bindings/sns/SnsOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SnsOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SnsOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"sns",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SnsOperationBindingVisitor;
