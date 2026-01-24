import { always } from "ramda";
import { Mixin } from "ts-mixer";
import OAuthFlowElement from "../../../../elements/OAuthFlow.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class OAuthFlowVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new OAuthFlowElement();
		this.specPath = always(["document", "objects", "OAuthFlow"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default OAuthFlowVisitor;
