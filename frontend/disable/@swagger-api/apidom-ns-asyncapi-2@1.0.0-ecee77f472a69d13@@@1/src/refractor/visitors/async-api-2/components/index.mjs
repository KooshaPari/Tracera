import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ComponentsElement from "../../../../elements/Components.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ComponentsVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsElement();
		this.specPath = always(["document", "objects", "Components"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ComponentsVisitor;
