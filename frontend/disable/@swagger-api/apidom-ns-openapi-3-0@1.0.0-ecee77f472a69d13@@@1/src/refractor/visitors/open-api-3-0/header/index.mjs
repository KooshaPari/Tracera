import { always } from "ramda";
import { Mixin } from "ts-mixer";
import HeaderElement from "../../../../elements/Header.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class HeaderVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new HeaderElement();
		this.specPath = always(["document", "objects", "Header"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default HeaderVisitor;
