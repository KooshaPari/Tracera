import { always } from "ramda";
import { Mixin } from "ts-mixer";
import OAuthFlowsElement from "../../../../elements/OAuthFlows.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class OAuthFlowsVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new OAuthFlowsElement();
		this.specPath = always(["document", "objects", "OAuthFlows"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default OAuthFlowsVisitor;
