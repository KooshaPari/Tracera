import { always } from "ramda";
import { Mixin } from "ts-mixer";
import DiscriminatorElement from "../../../../elements/Discriminator.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class DiscriminatorVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new DiscriminatorElement();
		this.specPath = always(["document", "objects", "Discriminator"]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default DiscriminatorVisitor;
