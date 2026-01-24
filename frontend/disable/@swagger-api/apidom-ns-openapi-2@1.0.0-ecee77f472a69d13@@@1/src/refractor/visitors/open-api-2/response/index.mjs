import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ResponseElement from "../../../../elements/Response.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ResponseVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ResponseElement();
		this.specPath = always(["document", "objects", "Response"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ResponseVisitor;
