import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SchemaElement from "../../../../elements/Schema.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SchemaVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new SchemaElement();
		this.specPath = always(["document", "objects", "Schema"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default SchemaVisitor;
