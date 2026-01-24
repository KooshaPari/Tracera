import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MessageExampleElement from "../../../../elements/MessageExample.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MessageExampleVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new MessageExampleElement();
		this.specPath = always(["document", "objects", "MessageExample"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default MessageExampleVisitor;
