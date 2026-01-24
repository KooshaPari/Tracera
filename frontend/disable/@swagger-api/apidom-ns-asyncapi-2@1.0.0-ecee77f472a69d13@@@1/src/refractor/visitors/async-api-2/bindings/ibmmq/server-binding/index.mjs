import { always } from "ramda";
import { Mixin } from "ts-mixer";
import IbmmqServerBindingElement from "../../../../../../elements/bindings/ibmmq/IbmmqServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class IbmmqServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new IbmmqServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ibmmq",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default IbmmqServerBindingVisitor;
