import { always } from "ramda";
import { Mixin } from "ts-mixer";
import Mqtt5MessageBindingElement from "../../../../../../elements/bindings/mqtt5/Mqtt5MessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class Mqtt5MessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new Mqtt5MessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"mqtt5",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default Mqtt5MessageBindingVisitor;
