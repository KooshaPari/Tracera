import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SnsServerBindingElement from "../../../../../../elements/bindings/sns/SnsServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SnsServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SnsServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"sns",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SnsServerBindingVisitor;
