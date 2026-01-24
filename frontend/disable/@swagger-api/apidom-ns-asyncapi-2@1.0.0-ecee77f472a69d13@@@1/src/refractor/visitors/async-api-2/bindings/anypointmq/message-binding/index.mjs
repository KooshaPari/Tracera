import { always } from "ramda";
import { Mixin } from "ts-mixer";
import AnypointmqMessageBindingElement from "../../../../../../elements/bindings/anypointmq/AnypointmqMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AnypointmqMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new AnypointmqMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"anypointmq",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default AnypointmqMessageBindingVisitor;
