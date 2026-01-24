import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MercureOperationBindingElement from "../../../../../../elements/bindings/mercure/MercureOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MercureOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MercureOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mercure",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MercureOperationBindingVisitor;
