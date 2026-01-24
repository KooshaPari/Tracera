import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SnsMessageBindingElement from "../../../../../../elements/bindings/sns/SnsMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SnsMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new SnsMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"sns",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default SnsMessageBindingVisitor;
