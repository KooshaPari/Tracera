import { always } from "ramda";
import { Mixin } from "ts-mixer";
import StompMessageBindingElement from "../../../../../../elements/bindings/stomp/StompMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class StompMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new StompMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"stomp",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default StompMessageBindingVisitor;
