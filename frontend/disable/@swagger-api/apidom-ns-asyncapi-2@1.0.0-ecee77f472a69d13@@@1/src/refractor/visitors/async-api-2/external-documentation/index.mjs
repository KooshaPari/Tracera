import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ExternalDocumentationElement from "../../../../elements/ExternalDocumentation.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ExternalDocumentationVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new ExternalDocumentationElement();
		this.specPath = always(["document", "objects", "ExternalDocumentation"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ExternalDocumentationVisitor;
