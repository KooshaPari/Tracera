import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MercureServerBindingElement from "../../../../../../elements/bindings/mercure/MercureServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MercureServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MercureServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mercure",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MercureServerBindingVisitor;
