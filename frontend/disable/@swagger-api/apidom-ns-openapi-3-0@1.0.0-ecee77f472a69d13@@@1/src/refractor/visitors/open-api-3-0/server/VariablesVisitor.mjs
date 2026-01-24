import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ServerVariablesElement from "../../../../elements/nces/ServerVariables.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class VariablesVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ServerVariablesElement();
		this.specPath = always(["document", "objects", "ServerVariable"]);
	}
}
export default VariablesVisitor;
