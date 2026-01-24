import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SecurityDefinitionsElement from "../../../../elements/SecurityDefinitions.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SecurityDefinitionsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	element;
	constructor(options) {
		super(options);
		this.element = new SecurityDefinitionsElement();
		this.specPath = always(["document", "objects", "SecurityScheme"]);
	}
}
export default SecurityDefinitionsVisitor;
