import { always } from "ramda";
import { Mixin } from "ts-mixer";
import LicenseElement from "../../../../elements/License.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class LicenseVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new LicenseElement();
		this.specPath = always(["document", "objects", "License"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default LicenseVisitor;
