import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ItemsElement from "../../../../elements/Items.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ItemsVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	specPath;
	canSupportSpecificationExtensions;
	constructor(options) {
		super(options);
		this.element = new ItemsElement();
		this.specPath = always(["document", "objects", "Items"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ItemsVisitor;
