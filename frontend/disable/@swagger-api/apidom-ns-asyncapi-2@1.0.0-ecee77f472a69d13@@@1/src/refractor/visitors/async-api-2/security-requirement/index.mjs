import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SecurityRequirementElement from "../../../../elements/SecurityRequirement.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SecurityRequirementVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new SecurityRequirementElement();
		this.specPath = always(["value"]);
	}
}
export default SecurityRequirementVisitor;
