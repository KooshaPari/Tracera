import { always } from "ramda";
import { Mixin } from "ts-mixer";
import OAuthFlowScopesElement from "../../../../elements/nces/OAuthFlowScopes.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ScopesVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new OAuthFlowScopesElement();
		this.specPath = always(["value"]);
	}
}
export default ScopesVisitor;
