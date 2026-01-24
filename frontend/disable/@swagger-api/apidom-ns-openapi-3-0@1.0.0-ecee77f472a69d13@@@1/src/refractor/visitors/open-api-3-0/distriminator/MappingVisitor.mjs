import { always } from "ramda";
import { Mixin } from "ts-mixer";
import DiscriminatorMappingElement from "../../../../elements/nces/DiscriminatorMapping.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MappingVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new DiscriminatorMappingElement();
		this.specPath = always(["value"]);
	}
}
export default MappingVisitor;
