import { always } from "ramda";
import { Mixin } from "ts-mixer";
import IbmmqOperationBindingElement from "../../../../../../elements/bindings/ibmmq/IbmmqOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class IbmmqOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new IbmmqOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ibmmq",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default IbmmqOperationBindingVisitor;
