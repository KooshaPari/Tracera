import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ChannelBindingsElement from "../../../../elements/ChannelBindings.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ChannelBindingsVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new ChannelBindingsElement();
		this.specPath = always(["document", "objects", "ChannelBindings"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ChannelBindingsVisitor;
