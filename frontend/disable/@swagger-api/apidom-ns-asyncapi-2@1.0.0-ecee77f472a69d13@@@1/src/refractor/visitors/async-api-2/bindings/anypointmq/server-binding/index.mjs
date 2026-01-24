import { always } from "ramda";
import { Mixin } from "ts-mixer";
import AnypointmqServerBindingElement from "../../../../../../elements/bindings/anypointmq/AnypointmqServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AnypointmqServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new AnypointmqServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"anypointmq",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default AnypointmqServerBindingVisitor;
