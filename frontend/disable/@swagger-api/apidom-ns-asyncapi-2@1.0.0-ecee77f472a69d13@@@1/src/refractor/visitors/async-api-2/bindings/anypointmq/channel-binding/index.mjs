import { always } from "ramda";
import { Mixin } from "ts-mixer";
import AnypointmqChannelBindingElement from "../../../../../../elements/bindings/anypointmq/AnypointmqChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class AnypointmqChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new AnypointmqChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"anypointmq",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default AnypointmqChannelBindingVisitor;
