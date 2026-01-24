import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ScopesElement from "../../../../elements/Scopes.mjs";
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
		this.element = new ScopesElement();
		this.specPath = always(["value"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ScopesVisitor;
