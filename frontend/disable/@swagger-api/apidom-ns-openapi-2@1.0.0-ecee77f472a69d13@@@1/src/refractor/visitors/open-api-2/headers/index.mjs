import { always } from "ramda";
import { Mixin } from "ts-mixer";
import HeadersElement from "../../../../elements/Headers.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class HeadersVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new HeadersElement();
		this.specPath = always(["document", "objects", "Header"]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default HeadersVisitor;
