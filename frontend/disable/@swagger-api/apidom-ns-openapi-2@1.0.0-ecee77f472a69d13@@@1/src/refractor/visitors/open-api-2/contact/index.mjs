import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ContactElement from "../../../../elements/Contact.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ContactVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ContactElement();
		this.specPath = always(["document", "objects", "Contact"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ContactVisitor;
