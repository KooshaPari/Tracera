import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MessageTraitElement from "../../../../elements/MessageTrait.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MessageTraitVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new MessageTraitElement();
		this.specPath = always(["document", "objects", "MessageTrait"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default MessageTraitVisitor;
