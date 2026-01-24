import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MercureMessageBindingElement from "../../../../../../elements/bindings/mercure/MercureMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MercureMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new MercureMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mercure",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default MercureMessageBindingVisitor;
