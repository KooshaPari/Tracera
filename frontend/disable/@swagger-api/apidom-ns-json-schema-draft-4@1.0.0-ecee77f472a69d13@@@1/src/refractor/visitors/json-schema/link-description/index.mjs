import { always } from "ramda";
import { Mixin } from "ts-mixer";
import LinkDescriptionElement from "../../../../elements/LinkDescription.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class LinkDescriptionVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new LinkDescriptionElement();
		this.specPath = always(["document", "objects", "LinkDescription"]);
	}
}
export default LinkDescriptionVisitor;
